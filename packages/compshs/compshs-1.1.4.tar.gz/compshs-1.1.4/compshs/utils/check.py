"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""

import re
import spacy
import sqlite3
from typing import Tuple


def load_lang(lang: str = 'en_core_web_sm'):
    """Load (trained) Spacy pipeline.

    Parameters
    ----------
    lang: str
        Spacy pipeline name (default is the english pipeline ``'en_core_web_sm'``).

    Returns
    -------
        Trained spacy pipeline, otherwise blank minimal pipeline.
    """
    try:
        return spacy.load(lang)
    except OSError as e:
        print(f'Error: {e} Failed to load Spacy pipeline {lang}.')
        print(f'Downloading the Spacy pipeline...')
        spacy.cli.download(lang)

        try:
            return spacy.load(lang)
        except OSError as e:
            print(f'Error: {e} Failed to load Spacy pipeline after download.')
            print(f'Fall back to minimal blank pipeline, i.e. tokenizer only.')
            return spacy.blank(lang)


def check_sql_identifier(identifier: str) -> str:
    """Ensure that an SQL identifier (table or column name) is safe to use in queries.

    Parameters
    ----------
    identifier: str
        Identifier name to check (column or table name).

    Returns
    -------
    str
        Identifier if valid.
    """
    if not re.fullmatch(r"[A-Za-z0-9_ ]+", identifier):
        raise ValueError(f'Invalid SQL identifier: {identifier}')
    return identifier


def check_sql_identifiers(identifiers: Tuple[str, ...]) -> Tuple[str, ...]:
    """Ensure that a list of SQL identifiers (table or column names) is safe to use in queries.

    Parameters
    ----------
    identifiers: List
        List of identifier names to check (column or table names).

    Returns
    -------
    list
        List of identifiers if valid.
    """
    return tuple(check_sql_identifier(ident) for ident in identifiers)


def check_exist_table_name(connection: sqlite3.Connection, table_name: str) -> bool:
    """Check whether a table exist in a database."""
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    exists = cursor.fetchone() is not None

    return exists


def check_exist_column_name(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Check whether a column exist in a table."""
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]

    return column_name in columns
