"""
Created in 2025
@author: Simon Delarue <simon.delarue@telecom-paris.fr>
"""
from contextlib import contextmanager
import sqlite3
from glob import glob
import os
from typing import Optional, Tuple

from compshs.data import Dataset
from compshs.utils import check_sql_identifiers, check_exist_table_name, check_exist_column_name


def from_directory(directory_path: str, dataset_name: str = None) -> Dataset:
    """Load a corpus from a directory containing text files.

    Parameters
    ----------
    directory_path: str
        Path to the directory containing text files (.txt).
    dataset_name: str
        Name of the returned Dataset. Directory name is used if not specified.

    Returns
    -------
    dataset: :class:`Dataset`

    Example
    -------
    >>> directory_path = 'path_to_txt_files'
    >>> dataset = from_directory(directory_path)
    >>> dataset.name
    'path_to_txt_files'
    """
    directory_path = os.path.expanduser(directory_path)
    txt_files = glob(os.path.join(directory_path, "*.txt"))

    corpus = []
    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            corpus.append(f.read())

    if dataset_name is None:
        dataset_name = os.path.basename(os.path.normpath(directory_path))

    return Dataset(name=dataset_name, corpus=corpus)


@contextmanager
def get_db_connection(database_path: str):
    conn = sqlite3.connect(os.path.expanduser(database_path))
    try:
        yield conn
    finally:
        conn.close()


def from_sql(database_path: str, dataset_name: str, table_name: str, document_column_name: str,
             document_name_field: str, document_text_field: str, filter_field: Optional[str] = None,
             excluded_value: Optional[str] = None, included_value: Optional[str] = None) -> Dataset:
    """Load a corpus from a sqlite database where documents are stored as JSON entries.

    Parameters
    ----------
    database_path: str
        Path to the `.db` file.
    dataset_name: str
        Name of the returned Dataset.
    table_name: str
        Name of the database table containing JSON documents.
    document_column_name: str
        Name of the table column containing JSON documents.
    document_name_field: str
        Name of the JSON field containing document label.
    document_text_field: str
        Name of the JSON field containing document textual content.
    filter_field: str, optional
        JSON key to filter by (default=None).
    excluded_value: str, optional
        Value to exclude from filtering the filter_field key (default=None).
    included_value: str, optional
        Value to include from filtering the filter_field key (default=None).

    Returns
    -------
        :class:`Dataset`
    """
    (table_name,
     document_column_name,
     document_name_field,
     document_text_field
     ) = check_sql_identifiers((
        table_name,
        document_column_name,
        document_name_field,
        document_text_field))

    with get_db_connection(database_path) as conn:
        cursor = conn.cursor()

        check_exist_table_name(conn, table_name)
        check_exist_column_name(conn, table_name, document_column_name)

        query, params = get_query(table_name, document_column_name, document_name_field, document_text_field,
                                  filter_field, excluded_value, included_value)

        # Execute query
        cursor.execute(query, params)

        corpus = cursor.fetchall()
        conn.close()

        if dataset_name is None:
            dataset_name = table_name

        return Dataset(name=dataset_name, corpus=corpus)


def get_query(table_name: str, document_column_name: str, document_name_field: str, document_text_field: str,
              filter_field: Optional[str] = None, excluded_value: Optional[str] = None,
              included_value: Optional[str] = None) -> Tuple:
    """
    Generate a parametrized SQL query.

    Parameters
    ----------
    table_name: str
        Name of the database table containing JSON documents.
    document_column_name: str
        Name of the table column containing JSON documents.
    document_name_field: str
        Name of the JSON field containing document label.
    document_text_field: str
        Name of the JSON field containing document textual content.
    filter_field: str, optional
        JSON key to filter by (default=None).
    excluded_value: str, optional
        Value to exclude from filtering the filter_field key (default=None).
    included_value: str, optional
        Value to include from filtering the filter_field key (default=None).

    Returns
    -------
    tuple
        Tuple of query and parameters.
    """
    if included_value is not None and excluded_value is not None:
        raise ValueError('Either included_value or excluded_value should be used, not both.')

    query = f'''
                SELECT
                    json_extract("{document_column_name}", '$.{document_name_field}') AS document_name,
                    json_extract("{document_column_name}", '$.{document_text_field}') AS txt
                FROM "{table_name}"
    '''

    params = ()

    if filter_field and excluded_value is not None:
        excluded_value = excluded_value.lower()
        query += f'''
            WHERE json_extract({document_column_name}, '$.{filter_field}') IS NULL
                OR LOWER(json_extract({document_column_name}, '$.{filter_field}')) != ?
        '''
        params = (excluded_value,)

    if filter_field and included_value is not None:
        included_value = included_value.lower()
        query += f'''
            WHERE json_extract({document_column_name}, '$.{filter_field}') IS NULL
                OR LOWER(json_extract({document_column_name}, '$.{filter_field}')) = ?
        '''
        params = (included_value,)

    return query, params
