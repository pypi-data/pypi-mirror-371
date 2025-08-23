"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import itertools
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def diversity(top_words: dict) -> float:
    """Diversity over topics.
    
    Parameters
    ----------
    top_words: dict
        Topic index as keys, top-word sets as values.
        
    Returns
    -------
    float
        Diversity.
    """
    unique_words = set()

    for s in top_words.values():
        unique_words |= s

    div = len(unique_words) / np.sum([len(s) for s in top_words.values()])

    return div


def topic_coherence(topic_words, dtm, vocab_index):
    """ Topic coherence as average NPMI over characteristic words of the topic. """
    scores = []

    n_docs = dtm.shape[0]

    for word_source, word_target in itertools.combinations(topic_words, 2):
        if word_source not in vocab_index or word_target not in vocab_index:
            continue

        docs_i = dtm[:, vocab_index[word_source]].toarray()
        docs_j = dtm[:, vocab_index[word_target]].toarray()

        p_i = docs_i.sum() / n_docs
        p_j = docs_j.sum() / n_docs
        p_ij = (docs_i & docs_j).sum() / n_docs

        if p_ij > 0:
            pmi = np.log(p_ij / (p_i * p_j))
            npmi = pmi / (-np.log(p_ij))
            scores.append(npmi)

    if len(scores) == 0:
        return 0
    else:
        return np.mean(scores)


def coherence(corpus: list, word_sets: dict) -> float:
    """Coherence over topics defined by word_sets.
    
    Parameters
    ----------
    corpus: list
        Corpus of documents.
    word_sets: dict
        Topic index as keys, word sets as values.
        
    Returns
    -------
    float
        Overall topic coherence.
    """
    vectorizer_bin = CountVectorizer(binary=True, ngram_range=(1, 2), token_pattern=r"(?u)\b[a-zA-Z]{4,}\b", max_features=30000)
    dtm_bin = vectorizer_bin.fit_transform(corpus)
    vocab = vectorizer_bin.get_feature_names_out()
    vocab_index = {word: i for i, word in enumerate(vocab)}

    coherences = []
    for i in range(len(word_sets)):
        topic_words = word_sets.get(i)
        coherence = topic_coherence(topic_words, dtm_bin, vocab_index)
        coherences.append(coherence)

    return coherence

def average_pairwise_similarity(values_source, values_target) -> float:
    r"""Average pairwise similarity between two arrays of values.
    
    Given two arrays of values :math:`I,J`, average pairwise similarity, denoted with
    :math:`psim(I,J)` is computed as: 
    
    .. math::
    
        psim(I,J)=\dfrac{\sum_{i\in I}\sum_{j \in J}sim(i,j)}{|I||J|}

    Parameters
    ----------
    value_source
        Array of values.
    value_target
        Array of values.

    Returns
    -------
    float
        Average pairwise similarity.
    """
    total_sim = np.sum([cosine_similarity(i.reshape(1, -1), j.reshape(1, -1)) for j in values_target for i in values_source])
    psim = total_sim / (len(values_source) * len(values_target))
    return psim
