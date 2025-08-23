import os
import tempfile
import unittest
import sqlite3
import json

from compshs.data.base import Dataset
from compshs.data.parse import from_directory, from_sql


class TestFromDirectory(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.test_dir.name
        self.file_contents = {'file1.txt': 'The quick brown fox.', 'file2.txt': 'The lazier dog.'}
        for filename, content in self.file_contents.items():
            with open(os.path.join(self.dir_path, filename), 'w', encoding='utf-8') as f:
                f.write(content)

    def test_from_directory_with_names(self):
        dataset_name = 'xyz'
        dataset = from_directory(self.dir_path, dataset_name)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.name, 'xyz')
        self.assertEqual(len(dataset.corpus), len(self.file_contents))
        self.assertCountEqual(dataset.corpus, list(self.file_contents.values()))

    def test_from_directory_without_names(self):
        dataset = from_directory(self.dir_path)

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.name, os.path.basename(self.dir_path))
        self.assertEqual(len(dataset.corpus), len(self.file_contents))
        self.assertCountEqual(dataset.corpus, list(self.file_contents.values()))

    def test_from_directory_empty(self):
        empty_dir = tempfile.TemporaryDirectory()
        dataset = from_directory(empty_dir.name, 'empty')

        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.name, 'empty')
        self.assertEqual(len(dataset.corpus), 0)
        empty_dir.cleanup()


class TestFromSQL(unittest.TestCase):

    cursor = None
    connection = None
    test_db_path = None

    @classmethod
    def setUpClass(cls):
        cls.test_db_fd, cls.test_db_path = tempfile.mkstemp(suffix='.db')
        cls.connection = sqlite3.connect(cls.test_db_path)
        cls.cursor = cls.connection.cursor()
        cls.cursor.execute('''
            CREATE TABLE test_table(
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        data = [
            json.dumps({'title': 'doc1', 'content': 'The quick brown fox.'}),
            json.dumps({'title': 'doc2', 'content': 'The lazier dog.'})
        ]

        cls.cursor.executemany('INSERT INTO test_table (data) VALUES (?)', [(d,) for d in data])
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()
        os.close(cls.test_db_fd)
        os.remove(cls.test_db_path)

    def test_01_from_sql_valid(self):
        dataset = from_sql(self.test_db_path, 'my_dataset_name', 'test_table', 'data', 'title', 'content')

        self.assertEqual(dataset.name, 'my_dataset_name')
        self.assertEqual(len(dataset.corpus), 2)
        self.assertEqual(dataset.corpus[0], ('doc1', 'The quick brown fox.'))
        self.assertEqual(dataset.corpus[1], ('doc2', 'The lazier dog.'))
        self.assertIsInstance(dataset, Dataset)

    def test_02_from_sql_default_dataset_name(self):
        dataset = from_sql(self.test_db_path, None, 'test_table', 'data', 'title', 'content')

        self.assertEqual(dataset.name, 'test_table')

    def test_03_from_sql_empty_table(self):
        self.cursor.execute('DROP TABLE test_table')
        self.cursor.execute('CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)')
        self.connection.commit()

        dataset = from_sql(self.test_db_path, 'empty_dataset', 'test_table', 'data', 'title', 'content')

        self.assertEqual(dataset.name, 'empty_dataset')
        self.assertEqual(len(dataset.corpus), 0)
