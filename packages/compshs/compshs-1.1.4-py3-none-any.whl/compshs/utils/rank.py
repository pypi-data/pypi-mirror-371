"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import numpy as np


def top_k(values: np.ndarray, k: int = 1) -> np.ndarray:
    """Returns indices of the k highest values.

    Parameters
    ----------
    values: np.ndarray
        Array of values.
    k: int
        Number of elements to return (default = 1).

    Returns
    -------
    np.ndarray
        Array of k indices.
    """
    if k >= len(values):
        return np.argsort(-values)
    else:
        return np.argpartition(-values, k)[:k]

def extract_top_words(viz_data, n_topics: int, lambdas: np.array, k: int) -> dict:
    """Extract top words for each topics in viz_data.
        Use relevance metric to select top_words.
        
    Parameters
    ----------
    viz_data
        Output from ``pyLDAvis`` library.
    n_topics: int
        Number of topics.
    lambdas: np.array
        Array of lamba values for relevance formula.
    k: int
        Top-k words are selected.
    
    Returns
    -------
    dict
        Dictionary with topic number as key and top words as values.
    """
    top_words = {}

    for topic_number in range(n_topics):
        top_words_topic = set()

        for lambda_ in lambdas:
            df_tmp = viz_data.sorted_terms(topic=topic_number + 1, _lambda=lambda_)
            top_words_tmp = set(df_tmp['Term'].values[:k])
            top_words_topic |= top_words_tmp

        top_words[topic_number] = top_words_topic
    
    return top_words
