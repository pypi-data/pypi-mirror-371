"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from typing import Tuple, Union

from compshs.text.base import BaseText


class FrequencyCounter(BaseText):
    """Counter of frequencies over corpus.

    Parameters
    ----------
    vectorizer_name: str
        Vectorizer name.
            - ``'token'``, Count of token occurrences over documents in corpus.
            - ``'tfidf'``, Tf-idf count over documents in corpus.
    ngram_range: Tuple
    analyzer: str
    max_df: float or int
    min_df: float or int
    """
    def __init__(self, vectorizer_name: str = 'tf', ngram_range: Tuple = (1, 1), analyzer: str = 'word',
                 max_df: Union[float, int] = 1.0, min_df: Union[float, int] = 1):
        super().__init__()
        self.vectorizer_name = vectorizer_name
        self.ngram_range = ngram_range
        self.analyzer = analyzer
        self.max_df = max_df
        self.min_df = min_df
        self.vectorizer = self._get_vectorizer(self.vectorizer_name, self.ngram_range, self.analyzer, self.max_df,
                                               self.min_df)

    def _get_vectorizer(self, vectorizer_name: str, ngram_range: Tuple, analyzer: str, max_df: Union[float, int],
                        min_df: Union[float, int]):
        """Get vectorizer.

        Parameters
        ----------
        vectorizer_name: str
            Vectorizer name.
                - ``'tf'``, Count of token occurrences over documents in corpus.
                - ``'tfidf'``, Tf-idf count over documents in corpus.
        ngram_range: Tuple
        analyzer: str
        max_df: float or int
        min_df: float or int
        
        Returns
        -------
        :class:`CountVectorizer()` or :class:`TfidfVectorizer`
        """
        if vectorizer_name == 'tf':
            return CountVectorizer(ngram_range=ngram_range, analyzer=analyzer, max_df=max_df, min_df=min_df)
        elif vectorizer_name == 'tfidf':
            return TfidfVectorizer(ngram_range=ngram_range, analyzer=analyzer, max_df=max_df, min_df=min_df)
        else:
            raise ValueError(f"Unknown vectorizer_name: {vectorizer_name}; must be in {'token', 'tfidf'}.")

    def fit(self, corpus: list) -> 'FrequencyCounter':
        """Fit algorithm to the corpus.

        Parameters
        ----------
        corpus: list
            List of (preprocessed) documents.

        Returns
        -------
        self: :class:`FrequencyCounter()`
        """
        self.vectorizer = self.vectorizer.fit(corpus)
        return self

    def transform(self, corpus: list) -> Tuple:
        """Compute frequencies over (preprocessed) corpus.

        Parameters
        ----------
        corpus: list
            List of (preprocessed) documents.

        Returns
        -------
        tuple
            Tuple of token names and frequencies matrix.
        """
        counts = self.vectorizer.transform(corpus)
        token_names = self.vectorizer.get_feature_names_out()

        return token_names, counts

    def fit_transform(self, corpus: list, *args, **kwargs):
        """Fit and transform data.

        Parameters
        ----------
        corpus: list
            List of (preprocessed) documents.

        Returns
        -------
        tuple
            Tuple of token names and frequencies matrix.
        """
        _ = self.fit(corpus)
        return self.transform(corpus)

    def get_token_names(self) -> np.ndarray:
        """Get token names.

        Returns
        -------
        np.ndarray
            Array of token names.
        """
        return self.vectorizer.get_feature_names_out()
