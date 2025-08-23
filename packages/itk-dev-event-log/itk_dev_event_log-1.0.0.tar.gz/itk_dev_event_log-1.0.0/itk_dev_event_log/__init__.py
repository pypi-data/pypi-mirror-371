"""This module allows event logging to a MSSQL-database."""

import pyodbc


TABLE_NAME = "itk_dev_event_log"
_connection_string = None  # pylint: disable=invalid-name


def setup_logging(connection_string: str):
    """Setup the logging module.
    Ensure the connection string is valid and that the logging table exists.

    Args:
        connection_string: The ODBC connection string to the database.
    """
    _ensure_table_exists(connection_string)
    global _connection_string  # pylint: disable=global-statement
    _connection_string = connection_string


def _ensure_table_exists(conn_str: str):
    """
    Ensures that a given table exists in the database. If not, it creates the table.

    Args:
        conn_str: ODBC connection string for SQL Server.
    """
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = ?
        """, (TABLE_NAME,))

        exists = cursor.fetchone()[0]

        if exists == 0:
            create_stmt = f"""
            CREATE TABLE [dbo].[{TABLE_NAME}] (
                [process_name] [varchar](50) NOT NULL,
                [timestamp] [datetime2](7) NOT NULL DEFAULT CURRENT_TIMESTAMP,
                [message] [varchar](100) NOT NULL,
                [count] [int] NOT NULL
            );
            """
            cursor.execute(create_stmt)


def emit(process_name: str, message: str, count: int = 1):
    """Emit a log message to the database.
    Remember to call setup_logging before calling this.

    Args:
        process_name: The name of the emitting process.
        message: The log message.
        count: An optional count. Defaults to 1.
    """
    assert _connection_string, "Logging not setup correctly. Remember to call setup_logging before emitting."

    with pyodbc.connect(_connection_string, autocommit=True) as conn:
        conn.execute(
            f"INSERT INTO {TABLE_NAME} (process_name, message, count) VALUES (?, ?, ?)",
            process_name,
            message,
            count
        )
