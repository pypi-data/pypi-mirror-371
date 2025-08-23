import unittest

from compshs.data.base import Dataset


class TestDataset(unittest.TestCase):
    def test_init(self):
        dataset = Dataset(name='xyz', test_key=[1, 2, 3])
        self.assertEqual(dataset.name, 'xyz')
        self.assertEqual(dataset.test_key, [1, 2, 3])

    def test_set_attr(self):
        dataset = Dataset()
        dataset.name = 'xyz'
        self.assertEqual(dataset.name, 'xyz')

    def test_get_attr(self):
        dataset = Dataset()
        with self.assertRaises(AttributeError):
            _ = dataset.non
