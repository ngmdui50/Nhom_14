import sqlite3
from contextlib import contextmanager

DB_NAME = "CSDLBTL.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Lỗi DB:", e)
    finally:
        conn.close()

def execute_query(query, params=()):
    with get_cursor() as cursor:
        cursor.execute(query, params)

def fetch_all(query, params=()):
    with get_cursor() as cursor:
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=()):
    with get_cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None