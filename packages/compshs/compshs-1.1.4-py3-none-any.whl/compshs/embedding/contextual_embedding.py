"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
from collections import defaultdict
import re
from tqdm import tqdm
import torch


class ContextualEmbedding():
    """Contextual embedding.
    
    Parameters
    ----------
    transformer
        Class objet for transformer model.
    model_name
        Model name to upload.
    tokenizer
        Class object for tokenizer.
    sentence_tokenizer
        Class object for sentence tokenizer.
    """
    def __init__(self, transformer, model_name, tokenizer, sentence_tokenizer):
        self.model_name = model_name
        self.transformer = transformer.from_pretrained(self.model_name)
        self.tokenizer = tokenizer.from_pretrained(self.model_name)
        self.sentence_tokenizer = sentence_tokenizer
        self.transformer.eval()

    def clean_text(self, text):
        """
        Text cleaning for contextual embedding use.
        """
        text = re.sub(r'(RR\\\d+EN\.docx|PE\d+\.\d+v\d+-\d+)', '', text)
        text = re.sub(r'?\d4/\d+?[A−Z]∗?\d4/\d+\(?[A−Z]∗??[A−Z]∗?\d{4}/\d+\(?[A-Z]*??', '', text)
        text = text.replace('\x0c', ' ')
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s{2,}', ' ', text)
        text = re.sub(r'\d+/\d+', '', text)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.{4,}', '', text)
        text = re.sub(r'-', '', text)
        text = text.strip()
        
        return text
    
    def extract_keyword_sentences(self, text, keywords, sentence_tokenizer):
        """Extract context for keywords.
        
        Parameters
        ----------
        text: str
            Documents from which context are extracted.
        keywords: list of str
            List of keywords.
        sentence_tokenizer
            Sentence tokenizer.
            
        Returns
        -------
        dict
            Dictionary of contexts:
                - keys: keywords
                - values: List of textual contexts in which the corresponding keyword appears.
        """
        keyword_contexts = defaultdict(list)

        sentences = sentence_tokenizer(text)
        
        for sentence in sentences:
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', sentence, re.IGNORECASE):
                    keyword_contexts[keyword].append(sentence)
                    
        return keyword_contexts

    def tokenize_and_chunk(self, text, tokenizer, max_length=512, stride=256):
        """Tokenize a text.
        
        When number of tokens is greater than max_length, result is split into chunks.

        Parameters
        ----------
        text: str
            Original text.
        tokenizer:
            Tokenizer.
        max_length: int
            Maximal number of tokens.
        stride: int
            Size of stride between token chunks. Useful in order not to lose contextual information when splitting tokens.
            
        Returns
        -------
        list
            List of :math:`n` dictionaries of tokens, with :math:`n` the number of chunks.
            Each dictionary contains:
                - input ids: tensor of ids of tokens in model vocabulary
                - attention_mask: tensor of values indicating if a token is real (1) or comes from padding (0)
                - offset_mapping: tensor indicating the start and end positions of each token within the original text.
        """
        tokens = tokenizer(
            text,
            return_offsets_mapping=True,
            return_attention_mask=True,
            return_tensors="pt",
            truncation=False,
            add_special_tokens=True
        )
        input_ids = tokens["input_ids"][0]
        attention_mask = tokens["attention_mask"][0]
        offset_mapping = tokens["offset_mapping"][0]

        chunks = []
        for i in range(0, len(input_ids), stride):
            input_chunk = input_ids[i:i + max_length]
            attention_chunk = attention_mask[i:i + max_length]
            offset_chunk = offset_mapping[i:i + max_length]
            
            if input_chunk.size(0) < max_length:
                pad_len = max_length - input_chunk.size(0)
                input_chunk = torch.cat([input_chunk, torch.full((pad_len,), tokenizer.pad_token_id)])
                attention_chunk = torch.cat([attention_chunk, torch.zeros(pad_len, dtype=torch.long)])
                offset_chunk = torch.cat([offset_chunk, torch.tensor([[0, 0]] * pad_len)])
            chunks.append({
                "input_ids": input_chunk.unsqueeze(0),
                "attention_mask": attention_chunk.unsqueeze(0),
                "offset_mapping": offset_chunk
            })
            
            if i + max_length >= len(input_ids):
                break
                
        return chunks

    def group_subword_embeddings(self, offset_mapping, embeddings, text, doc_id) -> list:
        """Average embeddings for splitted words.

        Parameters
        ----------
        offset_mapping: tensor
            Indicates the start and end positions of each token within the original text.
        embeddings
            Matrix of word embeddings
        text: str
            Original textual context.
        doc_id: int
            Id of the document in which word embeddings were computed.

        Returns
        -------
        list
            List of dictionaries containing:
                - doc id: id of the original document
                - word: word
                - position: position of word within original context
                - embedding: tensor representing the embedding of the word
                - context: textual context used for word embedding
        """
        cached_start = None
        cached_end = None
        word_embeddings = []
        subword_embeddings = []
        
        for (start, end), embedding in zip(offset_mapping, embeddings):
            if start == end:
                continue

            if cached_start is None:
                cached_start = start.item()
                cached_end = end.item()
                subword_embeddings = [embedding]
            elif start == cached_end:
                cached_end = end.item()
                subword_embeddings.append(embedding)
            else:
                word_text = text[cached_start:cached_end]
                avg_word_embedding = torch.stack(subword_embeddings).mean(dim=0)
                word_embeddings.append({
                    "doc_id": doc_id,
                    "word": word_text,
                    "position": (cached_start, cached_end),
                    "embedding": avg_word_embedding,
                    'context': text
                })

                cached_start = start.item()
                cached_end = end.item()
                subword_embeddings = [embedding]

        # Save last word embedding
        if subword_embeddings:
            word_text = text[cached_start:cached_end]
            avg_word_embedding = torch.stack(subword_embeddings).mean(dim=0)
            word_embeddings.append({
                "doc_id": doc_id,
                "word": word_text,
                "position": (cached_start, cached_end),
                "embedding": avg_word_embedding,
                'context': text
            })
                
        return word_embeddings

    def clean_word(self, word):
        word = re.sub(r'[^\w\s]', '', word)
        word = word.lower()
        return word
            
    def encode_chunk(self, model, chunk, text, doc_id):
        """Compute word embeddings for a chunk of text.
        
        Parameters
        ----------
        model
            Embedding model.
        chunk
            Chunk of tokenized text.
        text
            Original textual context.
        doc_id
            Id of the document.

        Returns
        -------
        list
            List of dictionaries containing:
                - doc id: id of the original document
                - word: word
                - position: position of word within original context
                - embedding: tensor representing the embedding of the word
                - context: textual context used for word embedding
        """
        with torch.no_grad():
            outputs = model(
                input_ids=chunk["input_ids"],
                attention_mask=chunk["attention_mask"]
            )
        embeddings = outputs.last_hidden_state.squeeze(0)
        offset_mapping = chunk["offset_mapping"]

        # Merge subword embeddings
        grouped_embeddings = self.group_subword_embeddings(offset_mapping, embeddings, text, doc_id)
        
        return grouped_embeddings
        
    def transform(self, corpus, keywords) -> list:
        """Performing contextual embedding of keywods within a corpus of documents.
        
        Parameters
        ----------
        corpus: list
            List of documents.
        keywords: list
            List of keywords to search and embed.

        Returns
        -------
        list
            A list of :math:`n` embedding dictionaries, with :math:`n` the number of documents in corpus.
        """
        all_embeddings = []

        for doc_id, document in tqdm(enumerate(corpus), total=len(corpus), desc='corpus'):
            embeddings = self.process_doc(document, doc_id, keywords)
            all_embeddings.append(embeddings)

        return all_embeddings
    
    def process_doc(self, document, doc_id, keywords) -> dict:
        """Processing a document consists in:
            - cleaning document
            - splitting in chunks (if necessary)
            - extracting context for each keyword
            - embedding keyword according to each specific context

        Parameters
        ----------
        document: str
            Textual document.
        keywords: list of str
            List of keywords to search and embed.
        doc_id: int
            Document id.
        keywords: list
            List of keywords to search and embed.

        Returns
        -------
        dict
            Dictionary of embeddings with the following structure:

            keyword_0 (STR):
                context_0 (STR):
                    word_0 (STR): embedding (tensor)
                    word_1 (STR): embedding (tensor)
                    ...
                context_1 (STR):
                    word_0 (STR): embedding (tensor)
                    word_1 (STR): embedding (tensor)
                    ...
                ...
            keyword_1 (STR):
                context_0 (STR):
                    word_0 (STR): embedding (tensor)
                    word_1 (STR): embedding (tensor)
                    ...
                context_1 (STR):
                    word_0 (STR): embedding (tensor)
                    word_1 (STR): embedding (tensor)
                    ...
                ...
            ...   
            
        """
        cleaned_text = self.clean_text(document)
        contexts = self.extract_keyword_sentences(cleaned_text, keywords, self.sentence_tokenizer)

        all_embeddings = {}
        
        for keyword, context_list in contexts.items():
            all_embeddings[keyword] = {}
            
            for i, context in enumerate(context_list):
                all_embeddings[keyword][context] = defaultdict(list)
                chunks = self.tokenize_and_chunk(context, self.tokenizer)
                
                for chunk in chunks:
                    word_embeddings = self.encode_chunk(self.transformer, chunk, context, doc_id)

                    # Case-insensitive
                    for word_embedding in word_embeddings:
                        all_embeddings[keyword][context][self.clean_word(word_embedding.get('word'))].append(word_embedding.get('embedding'))
        
                # Average word embeddings for all chunks within a context
                for k, v in all_embeddings[keyword][context].items():
                    all_embeddings[keyword][context][k] = torch.stack(v).mean(axis=0)

                # Average word embeddings for multi-word keywords
                subwords = keyword.split(' ')
                if len(subwords) > 1:
                    subword_embeddings = []
                    for subword in subwords:
                        # Punctuation can occur in embedded subwords; this allows to take into account punctuated subwords
                        for embedded_word in all_embeddings[keyword][context].keys():
                            if subword in embedded_word:
                                if not isinstance(all_embeddings[keyword][context][embedded_word], list):
                                    subword_embeddings.append(all_embeddings[keyword][context][embedded_word])
                    
                    avg_subword_embedding = torch.stack(subword_embeddings, dim=0).mean(axis=0)
                    all_embeddings[keyword][context][keyword] = avg_subword_embedding            

        return all_embeddings
