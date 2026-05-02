import sqlite3
from contextlib import contextmanager

DB_NAME = "CSDLBTL.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # Bật tính năng kiểm tra khóa ngoại của SQLite
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
        # Vẫn in ra Terminal để theo dõi
        print("❌ Lỗi DB:", e)
        # DÒNG QUAN TRỌNG NHẤT: Bắt buộc ném lỗi ra ngoài để main.py bắt được!
        raise e 
    finally:
        conn.close()

def execute_query(query, params=()):
    # Tự động tương thích với %s của MySQL sang ? của SQLite
    query = query.replace("%s", "?")
    with get_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount

def fetch_all(query, params=()):
    query = query.replace("%s", "?")
    with get_cursor() as cursor:
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=()):
    query = query.replace("%s", "?")
    with get_cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None