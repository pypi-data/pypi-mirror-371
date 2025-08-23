"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import itertools
import numpy as np
import pandas as pd

from compshs.semantics.base import BaseSemanticShift
from compshs.utils.metrics import average_pairwise_similarity


class SSTA(BaseSemanticShift):
    """Time-aware Self Similarity between word embeddings.

    .. math::

        SS_{TA}(w, a, k) = psim(I_{w,a,k}, I_{w,a,k+1})

    where:

        - :math:`w` is a word
        - :math:`a` is an attribute
        - :math:`k` is a timestep
    
    References
    ----------
    Soler, A. G., Labeau, M., & Clavel, C. (2023). Measuring lexico-semantic alignment in debates with contextualized word representations. In Proceedings of the First Workshop on Social Influence in Conversations (SICon 2023) (pp. 50-63). Association for Computational Linguistics.
    """
    def __init__(self):
        super().__init__()

    def attribute_exist_at_timedates(self, embeddings, attribute, 
                                     timedate_source, timedate_target) -> bool:
        """True if attribute exists in contextual embeddings at two reference timedates."""
        return attribute in embeddings.get(timedate_source) and attribute in embeddings.get(timedate_target)
    
    def keyword_exist_at_timedates(self, embeddings, keyword, attribute, 
                                   timedate_source, timedate_target) -> bool:
        """True if keyword exists in contextual embeddings at two reference timedates."""
        return keyword in embeddings.get(timedate_source).get(attribute) and keyword in embeddings.get(timedate_target).get(attribute)

    def transform(self, embeddings, timedates, attributes, keywords, 
                  group_embeddings: bool = True, group_output: bool = False, 
                  groups: list = None, group_names: list = None) -> pd.DataFrame:
        """Compute time-aware self similarity.
        
        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedates: np.ndarray
            Array of time values.
        attributes: np.ndarray
            Define subcorporas. Array of attribute values.
        keywords: list
            List of keywords.
        group_embeddings: bool
            If ``True``, group embeddings by timedate, attribute, keyword (default).
        group_output: bool
            If ``True``, group output dataframe using `groups`. Average is used for grouping.
        groups: list
            When group_output is set to ``True``, use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            When group_output is set to ``True``, use this parameter to rename groups of keywords.

        Returns
        -------
        :class:`pd.DataFrame()`
            DataFrame of time-aware similarities between embeddings at different timedates.
        """
        if group_embeddings:
            embeddings = self.group_embeddings(embeddings, timedates, attributes)

        unique_timedates = sorted(np.unique(timedates))
        unique_attributes = np.unique(attributes)
        df_psim = pd.DataFrame()

        for i in range(1, len(unique_timedates) - 1):
            if unique_timedates[i] in embeddings and unique_timedates[i - 1] in embeddings:
                for attribute in unique_attributes:
                    if self.attribute_exist_at_timedates(embeddings, attribute, unique_timedates[i], unique_timedates[i - 1]):
                        for keyword in keywords:
                            if self.keyword_exist_at_timedates(embeddings, keyword, attribute, unique_timedates[i], unique_timedates[i - 1]):
                                
                                # retrieve embeddings at source ant target timedates
                                emb_source = embeddings.get(unique_timedates[i - 1]).get(attribute).get(keyword)
                                emb_target = embeddings.get(unique_timedates[i]).get(attribute).get(keyword)

                                # compute pairwise similarity
                                psim = average_pairwise_similarity(emb_source, emb_target)
                                tmp = pd.DataFrame({
                                    'timedate': [unique_timedates[i]],
                                    'attribute': [attribute],
                                    'keyword': [keyword],
                                    'similarity': [psim]
                                })
                                df_psim = pd.concat([df_psim, tmp])
        
        if group_output:
            df_ssta_all = pd.DataFrame()
            for group, group_name in zip(groups, group_names):
                tmp = df_psim[df_psim['keyword'].isin(group)].copy()
                tmp = tmp.groupby(['timedate', 'attribute']).mean('similarity').reset_index()
                tmp['group'] = group_name
                df_ssta_all = pd.concat([df_ssta_all, tmp])
            return df_ssta_all

        return df_psim


class SApp(BaseSemanticShift):
    r"""Symmetric approaching between word embeddings.

    .. math::
    
        sApp(w) = psim(I_{w,a,k+1}, I_{w,a^{\prime},k+1}) - psim(I_{w,a,k}, I_{w,a^{\prime},k})
    
    where :math:`I_{w,a,k}` is the set of contextual embeddings of word :math:`w`, with attribute :math:`a`, at timestep :math:`k`.

    A positive value for :math:`sApp(w)` indicates that two subcorporas achieved a closer word semantics over time. Conversely, a negative value indicates that word representations diverged over time.
    
    References
    ----------
    Soler, A. G., Labeau, M., & Clavel, C. (2023). Measuring lexico-semantic alignment in debates with contextualized word representations. In Proceedings of the First Workshop on Social Influence in Conversations (SICon 2023) (pp. 50-63). Association for Computational Linguistics.
    """
    def __init__(self):
        super().__init__()
        self.metric_name = self.__class__.__name__.lower()

    def sapp_keywords_strategy(self, embeddings: list, attribute_x: str, attribute_y: str, timedate_x: str, timedate_y: str):
        """Compute intersection between sets of keywords at different timedates."""
        common_curr = self.get_common_keywords(embeddings, attribute_x, attribute_y, timedate_y, timedate_y)
        common_prev = self.get_common_keywords(embeddings, attribute_x, attribute_y, timedate_x, timedate_x)
        return common_curr.intersection(common_prev)
    
    def sapp_embeddings_strategy(self, embeddings: list, attribute_x: str, attribute_y: str, timedate_x: str, timedate_y: str, keyword: str):
        """Returns embeddings (embeddings for both attributes at current timedate, embeddings for both attributes at previous timedate)."""
        return (
            (embeddings[timedate_y][attribute_x][keyword], embeddings[timedate_y][attribute_y][keyword]),
            (embeddings[timedate_x][attribute_x][keyword], embeddings[timedate_x][attribute_y][keyword])
            )
    
    def compute_sapp_for_timepair(self, embeddings: list, timedate_source: str, timedate_target: str, attribute_x: str, attribute_y: str) -> list:
        """Compute sapp metric for a timepair.
        
        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedate_source: str
            Source timedate
        timedate_target: str
            Target timedate
        attribute_x: str
            First attribute
        attribute_y: str
            Second attribute

        Returns
        -------
        list
            List of dictionaries with metric information for all keywords.
        """
        return self.compute_metric_for_timepair(
            embeddings, timedate_source, timedate_target, attribute_x, attribute_y,
            keywords_strategy=self.sapp_keywords_strategy,
            embeddings_strategy=self.sapp_embeddings_strategy,
            metric_name=self.metric_name)

    def transform(self, embeddings: list, timedates: np.ndarray = None,
                  attributes: np.ndarray = None, group_embeddings: bool = True,
                  mode: str = 'sequential', time_pair: tuple = None,
                  group_output: bool = False, groups: list = None, group_names: list = None) -> pd.DataFrame:
        """Compute symmetric approaching for all available keywords and attributes in contextual embeddings.

        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedates: np.ndarray
            Array of time values.
        attributes: np.ndarray
            Define subcorporas. Array of attribute values.
        group_embeddings: bool
            If ``True``, group embeddings by timedate, attribute, keyword (default).
        mode: str
            ``'sequential'`` or ``'fixed'``.
        time_pair: tuple
            Tuple of timedates in str format (prev_time, curr_time), if mode = ``'fixed'``.
        group_output: bool
            If ``True``, group output dataframe using `groups`. Average is used for grouping.
        groups: list
            When group_output is set to ``True``, use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            When group_output is set to ``True``, use this parameter to rename groups of keywords.

        Returns
        -------
        :class:`pd.DataFrame()`
            DataFrame of symmetric approaching similarities between embeddings at different timedates. 
        """
        df_sapp = pd.DataFrame()

        if group_embeddings:
            embeddings = self.group_embeddings(embeddings, timedates, attributes)

        if mode=='sequential':
            unique_timedates = sorted(np.unique(timedates))
            time_pairs = [(unique_timedates[i - 1], unique_timedates[i]) for i in range(1, len(unique_timedates))]
        elif mode=='fixed':
            time_pairs = [time_pair]

        for prev_time, curr_time in time_pairs:

            if prev_time in embeddings and curr_time in embeddings:
                # sApp requires that word embeddings exist for both sectors at two timesteps
                common_attributes = self.get_common_attributes(embeddings, prev_time, curr_time)

                if len(common_attributes) > 2:

                    if mode=='sequential':
                        attribute_pairs = list(itertools.combinations(common_attributes, 2))
                    elif mode=='fixed':
                        attribute_pairs = list(itertools.product(common_attributes, repeat=2))
                    
                    for attribute_x, attribute_y in attribute_pairs:
                        if mode=='sequential':
                            attribute_x, attribute_y = sorted((attribute_x, attribute_y))

                        rows = self.compute_sapp_for_timepair(embeddings,
                                                               prev_time,
                                                               curr_time,
                                                               attribute_x,
                                                               attribute_y)
                        
                        df_sapp = pd.concat([df_sapp, pd.DataFrame(rows)], ignore_index=True)

        if group_output:
            if mode=='sequential':
                df_sapp = self.group_output_sequential(df_sapp,
                              metric=self.metric_name,
                              groups=groups,
                              group_names=group_names)
            elif mode=='fixed':
                df_sapp, self.ordered_keywords = self.group_output_fixed(df_sapp,
                              groups=groups,
                              group_names=group_names)

        return df_sapp
        

class AsApp(BaseSemanticShift):
    r"""Asymmetric Approaching between word embeddings.

    .. math::

        asApp(w, a) = psim(I_{w,a,t+1}, I_{w,a^{\\prime},t}) - psim(I_{w,a,t}, I_{w,a^{\\prime},t})
    
    where :math:`I_{w,a,t}` is the set of contextual embeddings of word :math:`w`, with attribute :math:`a`, at timestep :math:`t`.

    A positive value of :math:`asApp` indicates that attribute :math:`a` in the pair :math:`(a,a^{\prime})` has a recent (time :math:`t`) representation of a word :math:`w` that is close to the one initially used by attribute :math:`a^{\prime}` (time :math:`t-1`).

    A negative value of :math:`asApp` indicates that attribute :math:`a` in the pair :math:`(a,a^{\prime})` has a recent (time :math:`t`) representation of a word :math:`w` that moves away from the one initially used by attribute :math:`a^{\prime}` (time :math:`t-1`).

    References
    ----------
    Soler, A. G., Labeau, M., & Clavel, C. (2023). Measuring lexico-semantic alignment in debates with contextualized word representations. In Proceedings of the First Workshop on Social Influence in Conversations (SICon 2023) (pp. 50-63). Association for Computational Linguistics.
    """
    def __init__(self):
        super().__init__()
        self.metric_name = self.__class__.__name__.lower()

    def asapp_keywords_strategy(self, embeddings: list, attribute_x: str, attribute_y: str, timedate_x: str, timedate_y: str):
        """Compute intersection between sets of keywords at different timedates."""
        common_first = self.get_common_keywords(embeddings, attribute_x, attribute_y, timedate_y, timedate_x)
        common_second = self.get_common_keywords(embeddings, attribute_x, attribute_y, timedate_x, timedate_x)
        return common_first.intersection(common_second)
    
    def asapp_embeddings_strategy(self, embeddings: list, attribute_x: str, attribute_y: str, timedate_x: str, timedate_y: str, keyword: str):
        """Returns embeddings (embeddings for both attributes at current and previous timedates, embeddings for both attributes at previous timedate)."""
        return (
            (embeddings[timedate_y][attribute_x][keyword], embeddings[timedate_x][attribute_y][keyword]),
            (embeddings[timedate_x][attribute_x][keyword], embeddings[timedate_x][attribute_y][keyword])
            )

    def compute_asapp_for_timepair(self, embeddings: list, timedate_source: str, timedate_target: str, attribute_x: str, attribute_y: str) -> list:
        """Compute asapp metric for a timepair.
        
        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedate_source: str
            Source timedate
        timedate_target: str
            Target timedate
        attribute_x: str
            First attribute
        attribute_y: str
            Second attribute

        Returns
        -------
        list
            List of dictionaries with metric information for all keywords.
        """
        return self.compute_metric_for_timepair(
            embeddings, timedate_source, timedate_target, attribute_x, attribute_y,
            keywords_strategy=self.asapp_keywords_strategy,
            embeddings_strategy=self.asapp_embeddings_strategy,
            metric_name=self.metric_name)

    def transform(self, embeddings: list, timedates: np.ndarray = None,
                  attributes: np.ndarray = None, group_embeddings: bool = True,
                  mode: str = 'sequential', time_pair: tuple = None,
                  group_output: bool = False, groups: list = None, group_names: list = None) -> pd.DataFrame:
        """Compute asymmetric approaching for all available keywords and attributes in contextual embeddings.

        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedates: np.ndarray
            Array of time values.
        attributes: np.ndarray
            Define subcorporas. Array of attribute values.
        group_embeddings: bool
            If ``True``, group embeddings by timedate, attribute, keyword (default).
        mode: str
            ``'sequential'`` or ``'fixed'``.
        time_pair: tuple
            Tuple of timedates in str format (prev_time, curr_time), if mode = ``'fixed'``.
        group_output: bool
            If ``True``, group output dataframe using `groups`. Average is used for grouping.
        groups: list
            When group_output is set to ``True``, use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            When group_output is set to ``True``, use this parameter to rename groups of keywords.

        Returns
        -------
        :class:`pd.DataFrame()`
            DataFrame of asymmetric approaching similarities between embeddings at different timedates. 
        """
        df_asapp = pd.DataFrame()

        if group_embeddings:
            embeddings = self.group_embeddings(embeddings, timedates, attributes)

        if mode=='sequential':
            unique_timedates = sorted(np.unique(timedates))
            time_pairs = [(unique_timedates[i - 1], unique_timedates[i]) for i in range(1, len(unique_timedates))]
        elif mode=='fixed':
            time_pairs = [time_pair]

        for prev_time, curr_time in time_pairs:
            if prev_time in embeddings and curr_time in embeddings:
                # asApp requires that word embeddings exist for both attributes at two timesteps
                common_attributes = self.get_common_attributes(embeddings, curr_time, prev_time)

                if len(common_attributes) > 2:
                    attribute_pairs = list(itertools.product(common_attributes, repeat=2))
                    
                    for attribute_x, attribute_y in attribute_pairs:
                        # do not account for self comparisons between sectors
                        if attribute_x != attribute_y:

                            rows = self.compute_asapp_for_timepair(embeddings,
                                                                   prev_time,
                                                                   curr_time,
                                                                   attribute_x,
                                                                   attribute_y)
                        
                            df_asapp = pd.concat([df_asapp, pd.DataFrame(rows)], ignore_index=True)

        if group_output:
            if mode=='sequential':
                df_asapp = self.group_output_sequential(df_asapp,
                              metric=self.metric_name,
                              groups=groups,
                              group_names=group_names)
            elif mode=='fixed':
                df_asapp, self.ordered_keywords = self.group_output_fixed(df_asapp,
                              groups=groups,
                              group_names=group_names)
                
        return df_asapp
    

class DS(BaseSemanticShift):
    r"""Driving Strength between word embeddings.

    .. math::
    
        DS(w,a) = \dfrac{asApp(w,a)}{|asApp(w,a)|+|asApp(w,a^{\prime})|}
    
    Driving Strength is an asymmetric time-aware normalised measure indicating how much of the total approaching 
    between two subcorporas is done by one side.

    References
    ----------
    Soler, A. G., Labeau, M., & Clavel, C. (2023). Measuring lexico-semantic alignment in debates with contextualized word representations. In Proceedings of the First Workshop on Social Influence in Conversations (SICon 2023) (pp. 50-63). Association for Computational Linguistics.
    """
    def __init__(self):
        super().__init__()
        self.metric_name = self.__class__.__name__.lower()

    def transform(self, embeddings: list, timedates: np.ndarray = None,
                  attributes: np.ndarray = None, group_embeddings: bool = True,
                  time_pair: tuple = None,
                  groups: list = None, group_names: list = None) -> pd.DataFrame:
        """Compute driving strength metric for all available keywords and attributes in contextual embeddings.

        Parameters
        ----------
        embeddings: list
            List of Dictionaries of embeddings in the form of :meth:`ContextualEmbedding.transform()` output.
        timedates: np.ndarray
            Array of time values.
        attributes: np.ndarray
            Define subcorporas. Array of attribute values.
        group_embeddings: bool
            If ``True``, group embeddings by timedate, attribute, keyword (default).
        time_pair: tuple
            Tuple of timedates in str format (prev_time, curr_time).
        groups: list
            Use this parameter to group multiple keywords together. Expected format is a list of lists of keywords.
        group_names: list
            Use this parameter to rename groups of keywords.

        Returns
        -------
        :class:`pd.DataFrame()`
            DataFrame of driving strength similarities between embeddings at different timedates. 
        """
        df_ds = pd.DataFrame()
        rows = []

        asapp = AsApp()
        df_asapp = asapp.transform(embeddings, timedates, attributes, group_embeddings,
                                   'fixed', time_pair, True,
                                   groups, group_names)
        
        attribute_pairs = list(itertools.product(np.unique(attributes), repeat=2))
        for attribute_x, attribute_y in attribute_pairs:
            for keyword in asapp.ordered_keywords:
                asapp_x = df_asapp[((df_asapp['attribute_x']==attribute_x) & (df_asapp['attribute_y']==attribute_y)) & (df_asapp['keyword']==keyword)]['asapp']
                asapp_y = df_asapp[((df_asapp['attribute_x']==attribute_y) & (df_asapp['attribute_y']==attribute_x)) & (df_asapp['keyword']==keyword)]['asapp']

                if len(asapp_x) > 0 and len(asapp_y) > 0:
                    
                    # Compute DS
                    ds = asapp_x.item() / (np.abs(asapp_x.item()) + np.abs(asapp_y.item()))
                    
                    rows.append({
                        'timedate': time_pair[1],
                        'attribute_x': attribute_x,
                        'attribute_y': attribute_y,
                        'keyword': keyword,
                        self.metric_name: ds
                    })
                    
        df_ds = pd.concat([df_ds, pd.DataFrame(rows)], ignore_index=True)

        df_ds, self.ordered_keywords = self.group_output_fixed(df_ds,
                              groups=groups,
                              group_names=group_names)
                
        return df_ds
