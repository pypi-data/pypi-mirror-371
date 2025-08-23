"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import pandas as pd
import re
import scattertext as st
from scattertext import AssociationCompactor
import spacy
from spacy.tokens import Doc
from tqdm import tqdm

from compshs.text.base import BaseText


class FeatureSelection(BaseText):
    """Feature selection."""
    def __init__(self):
        super().__init__()
        self.formatted_corpus = None

    def get_df_from_corpus(self, corpus: list, attributes: list) -> pd.DataFrame:
        """Convert a list of documents with attribute information into a pandas DataFrame object.
        
        Parameters
        ----------
        corpus: list
            List of documents.
        attributes: list
            list (with same length as ``corpus``) of attributes.
            
        Returns
        -------
        :class:`pd.DataFrame()`
            DataFrame with corpus information.
        """
        df_corpus = pd.DataFrame()
        rows = []

        for i, (txt, attribute) in tqdm(enumerate(zip(corpus, attributes))):
            rows.append({
                'doc_id': i,
                'txt': txt,
                'attribute': attribute
            })
        df_corpus = pd.DataFrame(rows)
    
        return df_corpus

    def spacy_doc_from_txt(self, txt: str, input_type: str = 'words') -> Doc:
        r"""Create a Spacy :class:`Doc()` from text content.

        Note: Words with length :math:`\leq` 2 are filtered out.
        
        Parameters
        ----------
        txt: str
            Text content to convert.
        input_type: str
            - ``'words'``: ``txt`` contains only words separated by whitespaces. Useful in case of preprocessed text.
            - ``'sentences'``: ``txt`` contains sentences separated by commas. Useful in case of raw text.    
        
        Returns
        -------
        Spacy :class:`Doc()`.
        """
        nlp = spacy.blank("en")

        if input_type == "sentences":
            sentences = re.split(r'(?<=[.!?]) +', txt)
            tokenized_sentences = [sent.split() for sent in sentences if sent.strip()]

            words = []
            spaces = []
            sent_starts = []

            for sent in tokenized_sentences:
                for j, word in enumerate(sent):
                    if len(word) > 2:
                        words.append(word)
                        spaces.append(True)
                        sent_starts.append(j == 0)

            if spaces:
                spaces[-1] = False

            doc = Doc(nlp.vocab, words=words, spaces=spaces)

            for token, is_start in zip(doc, sent_starts):
                token.is_sent_start = is_start

        elif input_type == 'words':
            words = [w for w in txt.split() if len(w) > 2]
            spaces = [True] * len(words)
            if spaces:
                spaces[-1] = False

            doc = Doc(nlp.vocab, words=words, spaces=spaces)

            # the whole document is considered as a sentence
            for i, token in enumerate(doc):
                token.is_sent_start = (i == 0)

        return doc

    def transform(self, corpus: list, attributes: list, max_tokens: int = 2000, input_type: str = 'words'):
        """Transform corpus of documents into `scattertext` format using attribute information.
        
        Parameters
        ----------
        corpus: list
            List of documents.
        attributes: list
            list (with same length as ``corpus``) of attributes.
        max_tokens: int
            Maximum number of tokens to keep.
        input_type: str
            - ``'words'``: ``txt`` contains only words separated by whitespaces. Useful in case of preprocessed text.
            - ``'sentences'``: ``txt`` contains sentences separated by commas. Useful in case of raw text.   
        
        Returns
        -------
        :class:`scattertext` corpus.
        """
        print('Transforming data...')
        df_corpus = self.get_df_from_corpus(corpus, attributes)

        # convert corpus to Spacy Doc
        tqdm.pandas()
        df_corpus['parsed'] = df_corpus.txt.progress_apply(self.spacy_doc_from_txt)

        unigram_corpus = st.CorpusFromParsedDocuments(
            df_corpus,
            category_col='attribute',
            parsed_col='parsed'
        ).build(
            show_progress=True
        ).get_unigram_corpus(
        ).compact(AssociationCompactor(max_tokens))
        
        print('Done!')

        self.formatted_corpus = unigram_corpus
        
        return unigram_corpus
