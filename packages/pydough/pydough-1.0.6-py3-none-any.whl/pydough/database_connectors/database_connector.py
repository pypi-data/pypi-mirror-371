"""
PyDough implementation of a generic connection to database
by leveraging PEP 249 (Python Database API Specification v2.0).
https://peps.python.org/pep-0249/
"""
# Copyright (C) 2024 Bodo Inc. All rights reserved.

from dataclasses import dataclass
from enum import Enum

import pandas as pd

from .db_types import DBConnection, DBCursor

__all__ = ["DatabaseConnection", "DatabaseContext", "DatabaseDialect"]


class DatabaseConnection:
    """
    Class that manages a generic DB API 2.0 connection. This basically
    dispatches to the DB API 2.0 API on the underlying object and represents
    storing the state of the active connection.
    """

    # Database connection that follows DB API 2.0 specification.
    # sqlite3 contains the connection specification and is packaged
    # with Python.
    _connection: DBConnection

    def __init__(self, connection: DBConnection) -> None:
        self._connection = connection

    def execute_query_df(self, sql: str) -> pd.DataFrame:
        """Create a cursor object using the connection and execute the query,
        returning the entire result as a Pandas DataFrame.

        TODO: (gh #173) Support parameters. Dependent on knowing which Python
        types are in scope and how we need to test them.

        Args:
            `sql`: The SQL query to execute.

        Returns:
            list[pt.Any]: A list of rows returned by the query.
        """
        cursor: DBCursor = self._connection.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"ERROR WHILE EXECUTING QUERY:\n{sql}")
            raise e
        column_names: list[str] = [description[0] for description in cursor.description]
        # No need to close the cursor, as its closed by del.
        # TODO: (gh #174) Cache the cursor?
        # TODO: (gh #175) enable typed DataFrames.
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=column_names)

    # TODO: Consider adding a streaming API for large queries. It's not yet clear
    # how this will be available at a user API level.

    @property
    def connection(self) -> DBConnection:
        """
        Get the database connection. This API may be removed if all
        the functionality can be encapsulated in the DatabaseConnection.

        Returns:
            The database connection PyDough is managing.
        """
        return self._connection


class DatabaseDialect(Enum):
    """Enum for the supported database dialects.
    In general the dialects should"""

    ANSI = "ansi"
    SQLITE = "sqlite"
    MYSQL = "mysql"

    @staticmethod
    def from_string(dialect: str) -> "DatabaseDialect":
        """Convert a string to a DatabaseDialect enum.

        Args:
            `dialect`: The string representation of the dialect.

        Returns:
            The dialect enum.
        """
        dialect = dialect.upper()
        if dialect in DatabaseDialect.__members__:
            return DatabaseDialect.__members__[dialect]
        else:
            raise ValueError(f"Unsupported dialect: {dialect}")


@dataclass
class DatabaseContext:
    """
    Simple dataclass wrapper to manage the database connection and
    the required corresponding dialect.
    """

    connection: DatabaseConnection
    dialect: DatabaseDialect
