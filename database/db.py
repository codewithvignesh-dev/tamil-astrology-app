import sqlite3
from pathlib import Path
from typing import Optional

DATABASE_PATH = Path(__file__).resolve().parent / "horoscope.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS birth_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timezone TEXT NOT NULL,
            settings TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()
