from collections import defaultdict
import re
from tqdm.auto import tqdm

from compshs.text.base import BaseText
from compshs.utils import load_lang


class Preprocess(BaseText):
    """ Preprocessing of a corpus of documents.

    Parameters
    ----------
    lang: str
        Spacy language model name (``'en_core_web_sm'``).
    exclude_stop_words: bool
        If ``True``, exclude stopwords (default).
    exclude_punctuation: bool
        If ``True``, exclude punctuation (default).
    exclude_numbers: bool
        If ``True``, exclude numbers (default).
    lemmatize: bool
        If ``True``, lemmatize tokens (default).
    batch_size: int
        Number of documents to process in each batch (default = 10).
    chunk_size: int
        Maximum length of a piece of text. Beyond this length, the document is divided into chunks (default = 500000).
    nlp:
        Spacy model build upon ``lang`` parameter.
    """

    def __init__(self, lang: str = 'en_core_web_sm', exclude_stop_words: bool = True, exclude_punctuation: bool = True,
                 exclude_numbers: bool = True, lemmatize: bool = True, batch_size: int = 10, chunk_size: int = 500000):
        super().__init__()
        self.lang = lang
        self.exclude_stop_words = exclude_stop_words
        self.exclude_punctuation = exclude_punctuation
        self.exclude_numbers = exclude_numbers
        self.lemmatize = lemmatize
        self.batch_size = batch_size
        self.chunk_size = chunk_size
        self.nlp = None

    def _chunk_document(self, document: str) -> list:
        """Chunk a document into a list of subdocuments.

        Parameters
        ----------
        document: str
            Textual document.

        Returns
        -------
        list
            List of subdocuments, each of maximal length equals to ``chunk_size``.
        """
        return [document[i:i + self.chunk_size] for i in range(0, len(document), self.chunk_size)]

    def _clean_text(self, text: str) -> str:
        text = text.replace("-\n", "")
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\u200b\xa0]', ' ', text)
        text = re.sub(r"http\S+", "", text)
        # text = re.sub(r'(?<=\b) (?! )|(?<! ) (?=\b)', '', text)
        text = text.strip()
        return text

    def fit(self):
        """Fit algorithm to the data."""
        self.nlp = load_lang(self.lang)
        return self

    def transform(self, corpus: list) -> list:
        """Preprocess corpus:
            - remove stopwords
            - remove punctuation
            - remove numbers
            - extract lemmatized tokens
            - set tokens in lowercase

        Parameters
        ----------
        corpus: list
            List of documents.

        Returns
        -------
        list
            List of preprocessed documents.
        """
        indexed_chunks = []
        doc_indices = defaultdict(list)

        # Chunk large documents
        for i, document in enumerate(corpus):
            document = self._clean_text(document)
            chunks = self._chunk_document(document)
            for chunk in chunks:
                indexed_chunks.append((i, chunk))
                doc_indices[i].append(len(indexed_chunks) - 1)

        processed_chunks = []

        # Preprocess documents
        for document in tqdm(self.nlp.pipe((chunk for _, chunk in indexed_chunks), disable=['ner', 'parser'],
                                           batch_size=self.batch_size), desc='preprocessing'):
            tokens = []
            for token in document:
                if (self.exclude_stop_words and token.is_stop) or (self.exclude_punctuation and token.is_punct) or (self.exclude_numbers and (token.like_num or token.is_currency)):
                    continue

                if self.lemmatize:
                    transformed_token = token.lemma_.lower()
                else:
                    transformed_token = token.text.lower()

                tokens.append(transformed_token)

            processed_chunks.append(tokens)

        transformed_corpus = []

        # Merge chunked documents
        for i in range(len(corpus)):
            document_tokens = []
            for j in doc_indices[i]:
                document_tokens.extend(processed_chunks[j])
            transformed_corpus.append(" ".join(document_tokens))

        return transformed_corpus
