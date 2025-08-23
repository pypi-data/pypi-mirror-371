#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for check.py"""
import unittest
from unittest.mock import patch, MagicMock

from compshs.utils.check import *


class TestChecks(unittest.TestCase):

    @patch('spacy.load')
    def test_load_lang_success(self, mock_load):
        mock_load.return_value = 'Mocked Spacy Pipeline'

        result = load_lang('en_core_web_sm')

        self.assertEqual(result, 'Mocked Spacy Pipeline')
        mock_load.assert_called_once_with('en_core_web_sm')

    @patch('spacy.load')
    @patch('spacy.cli.download')
    def test_load_lang_fails_then_succeeds(self, mock_download, mock_load):
        # List of effects for loading (1st fail, 2nd success)
        mock_load.side_effect = [OSError('Mocked OSError'), 'Mocked Spacy Pipeline']

        result = load_lang('en_core_web_sm')

        self.assertEqual(result, 'Mocked Spacy Pipeline')
        mock_load.assert_called_with('en_core_web_sm')
        self.assertEqual(mock_load.call_count, 2)
        mock_download.assert_called_once_with('en_core_web_sm')

    @patch('spacy.load')
    @patch('spacy.cli.download')
    @patch('spacy.blank')
    def test_load_lang_downloads_and_loads_fail(self, mock_blank, mock_download, mock_load):
        # List of effects for loading (1st fail, 2nd fail)
        mock_load.side_effect = [OSError('1st Mocked OSError'), OSError('2nd Mocked OSError')]
        mock_download.return_value = None
        mock_blank.return_value = 'Mocked blank Spacy Pipeline'

        result = load_lang('en_core_web_sm')

        self.assertEqual(result, 'Mocked blank Spacy Pipeline')
        mock_download.assert_called_once_with('en_core_web_sm')
        # Verify that load was called twice
        self.assertEqual(mock_load.call_count, 2)
        # Verify that spacy.blank was called once
        self.assertEqual(mock_blank.call_count, 1)

    def test_check_sql_identifier(self):
        valid_identifier = 'valid_ident_123 '
        result = check_sql_identifier(valid_identifier)
        self.assertEqual(result, valid_identifier)

        invalid_identifier = 'invalid@'
        with self.assertRaises(ValueError):
            check_sql_identifier(invalid_identifier)

    def test_check_sql_identifiers(self):
        valid_identifiers = ('valid_ident_123', 'valid_ident_234', 'valid ident')
        result = check_sql_identifiers(valid_identifiers)
        self.assertEqual(result, valid_identifiers)

        mixed_identifiers = ('valid_ident', 'invalid@')
        with self.assertRaises(ValueError):
            check_sql_identifiers(mixed_identifiers)

        invalid_identifiers = ('invalid&', 'invalid@')
        with self.assertRaises(ValueError):
            check_sql_identifiers(invalid_identifiers)

        empty_identifiers = ()
        result = check_sql_identifiers(empty_identifiers)
        self.assertEqual(result, empty_identifiers)

    def test_check_exist_table_name(self):
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        self.connection.commit()

        result = check_exist_table_name(self.connection, 'test_table')
        self.assertTrue(result)

        result = check_exist_table_name(self.connection, 'fake_table')
        self.assertFalse(result)

        result = check_exist_table_name(self.connection, '')
        self.assertFalse(result)
        self.connection.close()

    def test_check_exist_column_name(self):
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        self.connection.commit()

        result = check_exist_column_name(self.connection, 'test_table', 'name')
        self.assertTrue(result)

        result = check_exist_column_name(self.connection, 'test_table', 'age')
        self.assertFalse(result)

        result = check_exist_column_name(self.connection, 'test_table', '')
        self.assertFalse(result)

        self.connection.close()
