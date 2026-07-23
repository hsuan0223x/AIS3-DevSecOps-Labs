import sqlite3
import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "lab.db")


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'bob', 'bob@example.com')")
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


def get_user_safe(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def search_user_by_name(username):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
