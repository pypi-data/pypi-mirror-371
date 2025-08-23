"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Tuple

from compshs.utils.metrics import average_pairwise_similarity


class BaseSemanticShift():
    """Base class for Semantic Shift Detection.

    Note: Semantic shift detection requires contextual word embeddings with additional attributes, e.g. time information.
    """
    def __init__(self):
        pass

    def group_embeddings(self, embeddings: list, timedates: np.ndarray, attributes: np.ndarray) -> dict:
        """Group dictionaries of contextual embeddings by:
        - time
        - attribute
        - keyword
        
        Parameters
        ----------
        embeddings: list
            List of dictionaries of embeddings in the form of :class:`ContextualEmbedding.transform()` output.
        timedates: np.ndarray
            Array of time values.
        attributes: np.ndarray
            Array of attribute values.

        Returns
        -------
        Single dictionary of keyword embeddings indexed by timedate, attribute, keyword.
        """
        grouped_embeddings = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for timedate, attribute, embedding in zip(timedates, attributes, embeddings):
            for keyword, contexts in embedding.items():
                for context, words in contexts.items():
                    context_emb = words.get(keyword)
                    if context_emb is not None:
                        grouped_embeddings[timedate][attribute][keyword].append(context_emb)

        return grouped_embeddings
    
    def get_common_keywords(self, embeddings: list, attribute_x: str, 
                            attribute_y: str, timedate_x: str, 
                            timedate_y: str) -> set:
        """Compute the set of common keywords between subcorporas at two timesteps and for two attributes."""
        common_keywords = set(embeddings.get(timedate_x).get(attribute_x)).intersection(embeddings.get(timedate_y).get(attribute_y))
        return common_keywords
    
    def get_common_attributes(self, embeddings: list, timedate_x: str, 
                              timedate_y: str) -> set:
        """Compute the set of common attributes between subcorporas at two different timesteps."""
        common_attributes = set(embeddings.get(timedate_x).keys()).intersection(embeddings.get(timedate_y).keys())
        return common_attributes
    
    def get_group(self, keyword, groups, group_names):
        for i, group in enumerate(groups):
            if keyword in group:
                return group_names[i]
        return 'NA'
    
    def group_output_sequential(self, similarities: pd.DataFrame, metric: str, groups: list, group_names: list) ->  pd.DataFrame:
        """Group approaching-based semantic detection output for sequential mode.
        
        Parameters
        ----------
        similarities: pd.DataFrame
            DataFrame containing approaching-based semantic similarities (see `shift.py` classes).
        metric: str
            Metric name.
        groups: list
            When group_output is set to ``True``, use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            When group_output is set to ``True``, use this parameter to rename groups of keywords.
        
        Returns
        -------
        Grouped similarities for approaching-based semantic detection methods.
        """
        df_output = pd.DataFrame()

        for group, group_name in zip(groups, group_names):
            tmp = similarities[similarities['keyword'].isin(group)].copy()
            tmp['label'] = tmp['attribute_x'] + ' x ' + tmp['attribute_y']
            tmp = tmp.groupby(['timedate', 'label']).mean(metric).reset_index()
            tmp['group'] = group_name
            df_output = pd.concat([df_output, tmp])
            
        return df_output

    def group_output_fixed(self, similarities: pd.DataFrame, groups: list, group_names: list) -> Tuple[pd.DataFrame, list]:
        """Group approaching-based semantic detection output for fixed mode.
        
        Parameters
        ----------
        similarities: pd.DataFrame
            DataFrame containing approaching-based semantic similarities (see `shift.py` classes).
        groups: list
            When group_output is set to ``True``, use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            When group_output is set to ``True``, use this parameter to rename groups of keywords.
        
        Returns
        -------
        Tuple of grouped similarities for approaching-based semantic detection methods and ordered keywords list.
        """
        ordered_keywords = [word for group in groups for word in group]
        similarities['group'] = similarities['keyword'].apply(lambda x: self.get_group(x, groups, group_names))
        
        return similarities, ordered_keywords
    
    def compute_metric_for_timepair(self, embeddings, timedate_source, timedate_target, attribute_x, attribute_y, keywords_strategy, embeddings_strategy, metric_name) -> list:
        """Generic computation for metrics between embeddings over time.
        
        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :class:`ContextualEmbedding.transform()` output.
        timedate_source: str
            Source timedate
        timedate_target: str
            Target timedate
        attribute_x: str
            First attribute
        attribute_y: str
            Second attribute
        keywords_strategy
            Strategy for selecting keyword intersection at different timedates.
        embeddings_strategy
            Strategy for selecting embeddings at different timedates.
        metric_name: str
            Metric name.

        Returns
        -------
        List of dictionaries with metric information for all keywords.
        """
        rows = []
        common_keywords = keywords_strategy(embeddings, attribute_x, attribute_y, timedate_source, timedate_target)

        for keyword in common_keywords:
            (vec_a, vec_b), (vec_c, vec_d) = embeddings_strategy(embeddings, attribute_x, attribute_y, timedate_source, timedate_target, keyword)

            psim_first = average_pairwise_similarity(vec_a, vec_b)
            psim_second = average_pairwise_similarity(vec_c, vec_d)

            rows.append({
                'timedate': timedate_target,
                'attribute_x': attribute_x,
                'attribute_y': attribute_y,
                'keyword': keyword,
                metric_name: psim_first - psim_second
            })

        return rows
    