"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
from collections import defaultdict
import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics.pairwise import pairwise_distances
import torch


class ConceptInduction():
    r"""Concept Induction (as a generalization of Word Sense Induction) framework from Lietard, et al. 2024.

    Original implementation is available at
    `<https://github.com/blietard/concept-induction>`_.

    Note: This class implements the bi-level approach.
    
    Parameters
    ----------
    local_params: dict
        Dictionary of local parameters. Keys must contain:
            - `mode`: Which linkage criterion to use in `sklearn`'s :class:`AgglomerativeClustering()` algorithm for local clustering (str, default = ``'average'``).
            - `nu`: Value of lobal :math:`\nu` hyperparameter (int)
    global_params: dict
        Dictionary of global parameters. Keys must contain:
            - `mode`: Which linkage criterion to use in `sklearn`'s :class:`AgglomerativeClustering()` algorithm for local clustering (str, default = ``'average'``.
            - `nu`: Value of global :math:`\nu` hyperparameter (int)
    distance: str
        Metric used for computing distance between clustered instances (default= `cosine`).

    References
    ----------
    Liétard, B., Denis, P., & Keller, M. (2024). To word senses and beyond: Inducing concepts with contextualized language models. arXiv preprint arXiv:2406.20054.
    """
    
    def __init__(self, local_params: dict, global_params: dict, distance: str = 'cosine'):
        self.local_params = local_params
        self.global_params = global_params
        self.distance = distance

    def group_embeddings(self, embeddings: list) -> dict:
        """Group a list of contextual embeddings by keywords.
        Using Lietard, et al. wording, it corresponds to contextutal occurrences of keywords.

        Parameters
        ---------
        embeddings: list
            Pre-computed contextual word embeddings stored in a list of :math:`n` elements, with :math:`n` the number of documents in corpus.
            
        Returns
        -------
        dict
            Dictionary of embeddings, with keyword as keys and list of contextual embeddings as values.
        """
        keyword_embeddings = defaultdict(list)

        for i, emb in enumerate(embeddings):
            for keyword, values in emb.items():
                for k, v in values.items():
                    if v.get(keyword) is not None:
                        keyword_embeddings[keyword].append(v.get(keyword))

        return keyword_embeddings
    
    def get_sense_clusters(self, keyword_embeddings: dict, nu: int, distance: str = 'cosine', mode: str = 'average') -> dict:
        r"""Compute locally estimated sense clusters (using sklearn :class:`AgglomerativeClustering` algorithm).
        
        Formally, from the set of contextual occurrences of keyword :math:`w`, denoted :math:`O^w`, it computes a partition :math:`S^w = \{ s_j^{w} \}_{1 \leq j \leq n_w}`.
        
        The set of all sense clusters of all keywords is the union of all partitions, :math:`\bigcup_{w \in W} S^{w}`.

        Parameters
        ----------
        keyword_embeddings: dict
            Dictionary of embeddings, with keyword as keys and list of contextual embeddings as values.
        nu: int
            Hyperparameter used in :math:`\tau = avg(d) - \nu std(d)`, with :math:`d` the distribution of distances
            between clustered instances.
        distance: str
            Distance metric computed between keyword embeddings (default = ``'cosine'``).
        mode: str
            Which linkage criterion to use in `sklearn`'s :class:`AgglomerativeClustering()` algorithm (default = ``'average'``).

        Returns
        -------
        dict
            Dictionary of sense clusters, with keywords as keys and lists of contextual embeddings as values.
        """
        
        # Compute distance between clustered instances
        print('Computing pairwise distances between keywords...')
        distances = dict()
        for keyword, embedding_list in keyword_embeddings.items():
            X = torch.stack(embedding_list).numpy()
            distances[keyword] = pairwise_distances(X, X, metric=distance)
        
        # Locally estimated sense clusters
        # Learn a partition of each O^w -> S^w
        sense_clusters = defaultdict(list)

        for keyword, embedding_list in keyword_embeddings.items():

            # Compute threshold tau
            dists = distances[keyword]
            mean_dist = dists.mean()
            std_dist = dists.std()
            tau = max(dists[dists.nonzero()].min(), mean_dist + nu * std_dist)

            X = torch.stack(embedding_list).numpy()
            clustering = AgglomerativeClustering(
                metric='precomputed',
                linkage=mode,
                distance_threshold=tau,
                n_clusters=None
            ).fit(dists)
            labels = clustering.labels_
            unique_labels = np.unique(labels)
            for label in unique_labels:
                sense_clusters[keyword].append(X[labels == label])

            print(f'Number of senses found for word {keyword} = {len(sense_clusters[keyword])}')

        return sense_clusters

    def average_senses(self, sense_clusters: dict) -> tuple:
        """Average embeddings in local sense clusters.
        
        Parameters
        ----------
        sense_clusters: dict
            Dictionary of sense clusters.
            
        Returns
        -------
        np.ndarray
            Array of average senses in clusters, original corresponding list of keywords.
        """
        
        # Stores original keyword
        keywords_origin = []
        # Stores avg senses
        avg_senses = []

        for keyword, senses in sense_clusters.items():
            for sense in senses:
                keywords_origin.append(keyword)
                # average senses over local cluster
                avg_sense = sense.mean(axis=0)
                avg_senses.append(avg_sense)
        
        return np.stack(avg_senses), keywords_origin

    def get_concept_clusters(self, senses, keywords_origin: list, nu: int, distance: str = 'cosine', mode: str = 'average'):
        r"""Compute globally estimated concept clusters.

        Formally, a concept :math:`c_k` is a cluster of senses, and :math:`C={c_k}_{1 \leq k \leq p}` is a partition of :math:`O` in :math:`p` concept clusters.
        
        Parameters
        ----------
        senses:
        keywords_origin: list
        nu: int:
            Hyperparameter used in :math:`\tau = avg(d) - \nu \times std(d)`, with :math:`d` the distribution of distances
            between clustered instances.
        distance: str
            Distance metric computed between senses (default = ``'cosine'``).
        mode: str
            Which linkage criterion to use in `sklearn`'s :class:`AgglomerativeClustering()` algorithm (default = ``'average'``).

        Returns
        -------
        list
            A list of concepts as a soft clustering over original keywords.
        """

        concepts = []

        print('Computing pairwise distances between senses...')
        distances = dict()
        distances = pairwise_distances(senses, senses, metric=distance)

        # Compute threshold tau
        mean_dist = distances.mean()
        std_dist = distances.std()
        tau = max(distances[distances.nonzero()].min(), mean_dist + nu * std_dist)

        clustering = AgglomerativeClustering(
            metric='precomputed',
            linkage=mode,
            distance_threshold=tau,
            n_clusters=None
        ).fit(distances)
        
        #clustering = AgglomerativeClustering(n_clusters=None,
        #                                        distance_threshold=6,
        #                                        linkage='average').fit(senses)
        labels = clustering.labels_
        unique_labels = np.unique(labels)

        for label in unique_labels:
            concepts.append(np.unique(np.asarray(keywords_origin)[labels == label]))

        return concepts
    
    def transform(self, embeddings, group_by_keywords: bool = True):
        """Perform concept induction given precomputed contextual embeddings.
        
        Parameters
        ----------
        embeddings
            Pre-computed contextual word embeddings.
        group_by_keywords: bool
            Set to ``True`` if `embeddings` are in the format of :meth:`ContextualEmbedding.transform()` output (default).
        
        Returns
        -------
        list
            A list of concepts as a soft clustering over original keywords.
        """
        if group_by_keywords:
            embeddings = self.group_embeddings(embeddings)

        # induce senses
        print('Inducting senses...')
        sense_clusters = self.get_sense_clusters(embeddings, self.local_params['nu'], self.distance, self.local_params['mode'])

        avg_senses, keywords_origin = self.average_senses(sense_clusters)

        # induce concepts
        print(f'Inducting concepts')
        concepts = self.get_concept_clusters(avg_senses, keywords_origin, self.global_params['nu'], self.distance, self.global_params['mode'])

        return concepts
