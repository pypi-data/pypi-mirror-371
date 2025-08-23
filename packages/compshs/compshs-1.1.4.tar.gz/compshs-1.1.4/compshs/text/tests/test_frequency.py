import numpy as np
import unittest
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from compshs.text.frequency import FrequencyCounter


class TestFrequency(unittest.TestCase):

    def setUp(self):
        self.corpus = ['The quick brown fox.', 'The dog is lazier.']

    def test_init_vectorizer(self):
        counter = FrequencyCounter(vectorizer_name='tf')
        self.assertIsInstance(counter.vectorizer, CountVectorizer)

        counter = FrequencyCounter(vectorizer_name='tfidf')
        self.assertIsInstance(counter.vectorizer, TfidfVectorizer)

        with self.assertRaises(ValueError):
            FrequencyCounter(vectorizer_name='toto')

    def test_fit_transform(self):
        counter = FrequencyCounter(vectorizer_name='tf')
        _ = counter.fit(self.corpus)
        self.assertTrue(len(counter.vectorizer.vocabulary_) >= 0)

        token_names, counts = counter.transform(self.corpus)
        self.assertEqual(len(token_names), counts.shape[1])
        self.assertEqual(counts.shape[0], len(self.corpus))

        token_names, counts = counter.fit_transform(self.corpus)
        self.assertEqual(len(token_names), counts.shape[1])
        self.assertEqual(counts.shape[0], len(self.corpus))

    def test_get_token_names(self):
        counter = FrequencyCounter(vectorizer_name='tf')
        _ = counter.fit(self.corpus)
        token_names = counter.get_token_names()
        self.assertIsInstance(token_names, np.ndarray)
        self.assertTrue(len(token_names) >= 0)
