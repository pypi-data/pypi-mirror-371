"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import numpy as np
from scipy import sparse
from sklearn.decomposition import LatentDirichletAllocation, NMF
from typing import Tuple, Union

from compshs.text.base import BaseText


class TopicModeler(BaseText):
    """Topic modeler.

    Parameters
    ----------
    model_name: str
        Model name.
            - ``'LDA'``, Latent Dirichlet Allocation.
            - ``'NMF'``, Non-Negative Matrix Factorization.
    n_components: int
        Number of topics.
    """
    def __init__(self, model_name: str = 'LDA', n_components: int = 10):
        super().__init__()
        self.model_name = model_name
        self.n_components = n_components
        self.modeler = self._get_modeler(self.model_name, self.n_components)

    @staticmethod
    def _get_modeler(model_name: str, n_components: int):
        """Get modeler.

        Parameters
        ----------
        model_name: str
            Model name.
                - ``'LDA'``, Latent Dirichlet Allocation.
                - ``'NMF'``, Non-Negative Matrix Factorization.
        n_components: int
            Number of topics.

        Returns
        -------
        :class:`LatentDirichletAllocation` or :class:`NMF()`.
        """
        if model_name == 'LDA':
            return LatentDirichletAllocation(n_components=n_components)
        elif model_name == 'NMF':
            return NMF(n_components=n_components)
        else:
            raise ValueError(f"Unknown model_name: {model_name}; must be in {'LDA', 'NMF'}.")

    def fit(self, matrix: Union[sparse.csr_matrix, np.ndarray]) -> 'TopicModeler':
        """Fit algorithm to the document term matrix.

        Parameters
        ----------
        matrix: sparse.csr_matrix, np.ndarray
            Document term matrix (n_documents, n_words).

        Returns
        -------
        self: :class:`TopicModeler`
        """
        self.modeler = self.modeler.fit(matrix)
        return self

    def transform(self, matrix: Union[sparse.csr_matrix, np.ndarray]) -> Tuple:
        """Transform data according to the fitted model.

        Parameters
        ----------
        matrix: sparse.csr_matrix, np.ndarray
            Document term matrix (n_documents, n_words).

        Returns
        -------
        tuple
            Tuple of topic names and document topic distribution matrix (n_samples, n_components).
        """
        topic_distribution = self.modeler.transform(matrix)
        topic_names = self.modeler.get_feature_names_out()

        return topic_names, topic_distribution

    def fit_transform(self, matrix: Union[sparse.csr_matrix, np.ndarray], *args, **kwargs) -> Tuple:
        """Fit and transform data.

        Parameters
        ----------
        matrix: sparse.csr_matrix, np.ndarray
            Document term matrix (n_documents, n_words).

        Returns
        -------
        tuple
            Tuple of topic names and document topic distribution matrix (n_documents, n_components).
        """
        _ = self.fit(matrix)
        return self.transform(matrix)

    def get_word_contributions(self) -> np.ndarray:
        """Get matrix of word (n_components, n_words) contributions to each topic."""
        return self.modeler.components_
