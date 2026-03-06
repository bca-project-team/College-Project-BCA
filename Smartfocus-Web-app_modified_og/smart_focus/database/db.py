import sqlite3
import os

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "smartfocus.db")

def init_db():

    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user TEXT,
        mode TEXT,
        activity TEXT,
        goal_hours REAL,
        focused_seconds INTEGER,
        distracted_seconds INTEGER,
        focused_minutes INTEGER,
        focus_score INTEGER,
        goal_achieved INTEGER,
        total_seconds INTEGER
    )
    """)

    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_PATH)