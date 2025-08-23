import unittest

from compshs.text.preprocess import Preprocess


class TestPreprocess(unittest.TestCase):

    def setUp(self):
        self.preprocessor = Preprocess(lang='en_core_web_sm')
        self.preprocessor.fit()
        self.corpus = ['The quick brown fox.', 'The dog is lazier.']

    def test_fit(self):
        self.assertIsNotNone(self.preprocessor.nlp, 'Model should be loaded after calling .fit().')

    def test_transform(self):
        # Default settings
        result = self.preprocessor.transform(self.corpus)
        self.assertEqual(len(result), 2)
        for doc in result:
            self.assertTrue(all(isinstance(token, str) for token in doc))
            self.assertNotIn('is', doc)
            self.assertNotIn('.', doc)
            self.assertNotIn('lazier', doc)

        # Including stopwords
        self.preprocessor = Preprocess(lang='en_core_web_sm', exclude_stop_words=False)
        self.preprocessor.fit()
        result = self.preprocessor.transform(self.corpus)
        self.assertIn('the', result[0])

        # Punctuation included
        self.preprocessor = Preprocess(lang='en_core_web_sm', exclude_punctuation=False)
        self.preprocessor.fit()
        result = self.preprocessor.transform(self.corpus)
        self.assertIn('.', result[0])

        # Without lemmatization
        self.preprocessor = Preprocess(lang='en_core_web_sm', lemmatize=False)
        self.preprocessor.fit()
        result = self.preprocessor.transform(self.corpus)
        self.assertIn('lazier', result[1])

        # Empty corpus
        result = self.preprocessor.transform([])
        self.assertEqual(result, [])

        # Batch size
        self.preprocessor = Preprocess(lang='en_core_web_sm', batch_size=2)
        self.preprocessor.fit()
        result = self.preprocessor.transform(self.corpus)
        self.assertEqual(len(result), len(self.corpus))
