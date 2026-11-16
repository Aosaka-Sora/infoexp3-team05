
import sqlite3
from pathlib import Path

DB = Path("data/words.db")


# データベースに接続
def connect():
    DB.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB)


# テーブルを作成
def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                japanese TEXT NOT NULL
            )
        """)


# 単語を登録
def add_word(english, japanese):
    with connect() as con:
        con.execute(
            "INSERT INTO words (english, japanese) VALUES (?, ?)",
            (english, japanese)
        )


# 単語をすべて取得
def get_words():
    with connect() as con:
        rows = con.execute(
            "SELECT english, japanese FROM words"
        ).fetchall()

    return rows
