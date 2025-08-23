#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for plot.py"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy import sparse
import unittest

from compshs.text import TopicModeler
from compshs.visualization.plot import plot_top_words, plot_pyLDA


class TestPlot(unittest.TestCase):

    def setUp(self):
        self.matrix = sparse.identity(5)
        self.n_components = 2
        topic_modeler = TopicModeler(model_name='LDA', n_components=self.n_components)
        self.topic_modeler = topic_modeler.fit(self.matrix)
        self.token_names = np.array(['fox', 'cat', 'dog', 'brown', 'quick'])
    
    def test_plot_top_words(self):
        fig = plot_top_words(self.topic_modeler, self.token_names, k=2, title='Title')

        self.assertIsInstance(fig, Figure)

        # number of subplots corresponds to number of topics
        self.assertEqual(len(fig.axes), self.n_components)
        plt.close(fig)

        fig = plot_top_words(self.topic_modeler, self.token_names, k=2, title=None)
        self.assertTrue(fig.get_suptitle()==self.topic_modeler.model_name)
        plt.close(fig)

    def test_plot_pyLDA(self):
        pass

    def test_plot_ssta(self):
        pass

    def test_plot_sequential_approaching(self):
        pass

    def test_plot_fixed_approaching(self):
        pass

    def test_plot_feature_selection(self):
        pass
