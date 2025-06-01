import sqlite3

DB_NAME = "catalog.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            duration INTEGER NOT NULL,
            views INTEGER DEFAULT 0,
            genre TEXT
        )
    ''')
    conn.commit()
    conn.close()