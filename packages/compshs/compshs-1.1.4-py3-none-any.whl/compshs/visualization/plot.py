"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import os
import pandas as pd
import pyLDAvis
import pyLDAvis.lda_model
import scattertext as st
from scattertext import produce_scattertext_explorer
from scipy import sparse
from typing import Union
import webbrowser

from compshs.text import FrequencyCounter, TopicModeler
from compshs.utils import top_k


def plot_top_words(topic_modeler: TopicModeler, token_names: np.ndarray, k: int = 5, title: str = None) -> Figure:
    """Plot top :math:`k` tokens in each modeled topic.

    Parameters
    ----------
    topic_modeler: :class:`TopicModeler`
        Fitted topic modeler.
    token_names: np.ndarray
        Array of token names.
    k: int
        Number of tokens displayed per topic (default = 5).
    title: str
        Plot title. If ``None``, the name of the model is used.

    Returns
    -------
    Figure

    References
    ----------
    Scikit-learn documentation (see `<https://scikit-learn.org/stable/lite/lab/index.html>`_).
    """
    fig, axes = plt.subplots(1, topic_modeler.n_components, figsize=(30, 15), sharex=True)
    axes = axes.flatten()

    for topic_idx, words_contributions in enumerate(topic_modeler.get_word_contributions()):
        top_token_indices = top_k(words_contributions, k)
        top_token_names = token_names[top_token_indices]
        values = words_contributions[top_token_indices]

        ax = axes[topic_idx]
        ax.barh(top_token_names, values, height=0.7)
        ax.set_title(f"Topic {topic_idx + 1}", fontdict={"fontsize": 30})
        ax.tick_params(axis="both", which="major", labelsize=20)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        if title is None:
            title = topic_modeler.model_name
        fig.suptitle(title, fontsize=40)

    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)

    return fig

def plot_pyLDA(topic_modeler: TopicModeler, matrix: Union[sparse.csr_matrix, np.ndarray], counter: FrequencyCounter):
    """ Plot LDA using pyLDAvis library.

    Parameters
    ----------
    topic_modeler: :class:`TopicModeler`
        Fitted topic modeler.
    matrix: sparse.csr_matrix, np.ndarray
        Document term matrix (n_documents, n_words).
    counter: :class:`FrequencyCounter`
        Frequency counter.

    Returns
    -------
    Visualization object.
    """
    if topic_modeler.model_name == 'LDA':
        viz_data = pyLDAvis.lda_model.prepare(topic_modeler.modeler, matrix, counter.vectorizer)
        return viz_data
    else:
        raise Exception

def plot_ssta(similarities: pd.DataFrame):
    """Plot SSTA.
    
    Parameters
    ----------
    similarities: pd.DataFrame
        DataFrame of embedding similarities (such as :meth:`SSTA.transform()` output).
    """
    lines = alt.Chart(similarities).mark_line(point=True).encode(
        x=alt.X('timedate:O', title=''),
        y=alt.Y('similarity:Q', title="Self similarity"),
        color=alt.Color('group:N').legend(None)
    )

    base_chart = alt.layer(lines).properties(
        width=150,
        height=70,
    )

    # Facet : sector en colonne, concept en ligne
    chart = base_chart.facet(
        column=alt.Column('attribute:N', title=None),
        row=alt.Row('group:N', title=None)
    )

    output_path = os.path.abspath('ssta_plot.html')
    chart.save(output_path)
    print(f'Chart saved here : {output_path}')

    webbrowser.open('file://' + output_path)


def plot_sequential_approaching(similarities: pd.DataFrame, metric: str = 'sapp'):
    """Heatmap for approaching-based semantic shift results in sequential mode.
    
    Parameters
    ----------
    similarities: pd.DataFrame
        Semantic shift detection results.
    metric: str
        Name of semantic shift detection metric to plot ({``'sapp'``, ``'asapp'``}).
    """

    base = alt.Chart(similarities).mark_rect(stroke='white', strokeWidth=1).encode(
        x=alt.X('timedate:O', title='Year'),
        y=alt.Y('label:N', title='',
                axis=alt.Axis(labelAngle=0, labelLimit=400, labelFontSize=10)),
        color=alt.Color(f'{metric}:Q', title=metric,
                        scale=alt.Scale(scheme='redblue', type='sqrt', reverse=True)),
        tooltip=['timedate', 'label', 'group', metric]
    ).properties(
        width=150,
        height=300
    )

    # Facet grid per group
    facet = base.facet(
        facet=alt.Facet('group:N', title=''),
        columns=3
    )
    output_path = os.path.abspath(f'{metric}_plot_sequential.html')
    facet.save(output_path)
    print(f'Chart saved here : {output_path}')

    webbrowser.open('file://' + output_path)


def plot_fixed_approaching(similarities: pd.DataFrame, metric: str, keyword_order: list, keyword_colors: dict):
    """Barchart for approaching-based semantic shift detection results for fixed mode.
    
    Parameters
    ----------
    similarities: pd.DataFrame
        Semantic shift detection results.
    metric: str
        Name of semantic shift detection metric to plot ({``'sapp'``, ``'asapp'``}).
    keyword_order: list
        Legend ordering.
    keyword_colors: dict
        Dictionary with keywords as keys and corresponding colour as values (both str).
    """

    bars = alt.Chart(similarities).mark_bar().encode(
        y=alt.Y('keyword:O', title='', sort=keyword_order),
        x=alt.X(f'{metric}:Q', title=metric),
        color=alt.Color("keyword:N",
                        sort=keyword_order,
                        scale=alt.Scale(domain=list(keyword_colors.keys()), range=list(keyword_colors.values()))
                    )
    )

    base_chart = alt.layer(bars).properties(
        width=250,
        height=230,
    )

    chart = base_chart.facet(
        row=alt.Row("attribute_x:N").title("Sector").header(labelAngle=0),
        column=alt.Column("attribute_y:N").title("Sector"),
        title=f'{metric} between fixed dates.'
        
    )
    output_path = os.path.abspath(f'{metric}_plot_fixed.html')
    chart.save(output_path)
    print(f'Chart saved here : {output_path}')

    webbrowser.open('file://' + output_path)
    

def plot_feature_selection(corpus, category, category_name, not_category_name, min_term_frequency):
    """Plot feature selection in html using ``ScatterText`` library.
    
    Parameters
    ----------
    corpus:
    category:
    category_name:
    not_category_name:
    min_term_frequency:
    """
    html = produce_scattertext_explorer(
        corpus,
        category=category,
        category_name=category_name,
        not_category_name=not_category_name,
        minimum_term_frequency=min_term_frequency,
        width_in_pixels=1000,
        term_significance=st.LogOddsRatioUninformativeDirichletPrior()
    )
    filename = 'feature_selection_plot.html'
    open(filename, 'wb').write(html.encode('utf-8'))
