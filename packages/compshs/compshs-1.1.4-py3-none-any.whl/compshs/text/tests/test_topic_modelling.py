import numpy as np
from sklearn.decomposition import LatentDirichletAllocation, NMF
from scipy import sparse
import unittest

from compshs.text.topic_modelling import TopicModeler


class TestTopicModelling(unittest.TestCase):

    def setUp(self):
        self.matrix = sparse.identity(3)

    def test_init_topic_modeler(self):
        topic_modeler = TopicModeler(model_name='LDA')
        self.assertIsInstance(topic_modeler.modeler, LatentDirichletAllocation)

        topic_modeler = TopicModeler(model_name='NMF')
        self.assertIsInstance(topic_modeler.modeler, NMF)

        with self.assertRaises(ValueError):
            TopicModeler(model_name='toto')

    def test_fit_transform(self):
        topic_modeler = TopicModeler(model_name='LDA')
        _ = topic_modeler.fit(self.matrix)
        self.assertTrue(np.any(topic_modeler.modeler.components_ != 0))

        topic_names, topic_distribution = topic_modeler.transform(self.matrix)
        self.assertEqual(len(topic_names), topic_distribution.shape[1])
        self.assertEqual(topic_distribution.shape[0], self.matrix.shape[0])

        topic_names, topic_distribution = topic_modeler.fit_transform(self.matrix)
        self.assertEqual(len(topic_names), topic_distribution.shape[1])
        self.assertEqual(topic_distribution.shape[0], self.matrix.shape[0])

    def test_get_word_contributions(self):
        topic_modeler = TopicModeler(model_name='LDA')
        _ = topic_modeler.fit(self.matrix)
        word_contributions = topic_modeler.get_word_contributions()
        self.assertIsInstance(word_contributions, np.ndarray)
        self.assertTrue(len(word_contributions) >= 0)
