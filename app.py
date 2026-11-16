import random
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
WORD_DB = Path("data/word.db")


def read_words():
    if not WORD_DB.exists():
        raise FileNotFoundError

    with sqlite3.connect(WORD_DB) as con:
        rows = con.execute(
            "SELECT english, japanese FROM words "
            "WHERE english IS NOT NULL AND japanese IS NOT NULL "
            "ORDER BY rowid"
        ).fetchall()

    return [
        (str(english).strip(), str(japanese).strip())
        for english, japanese in rows
        if str(english).strip() and str(japanese).strip()
    ]


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/quiz")
def get_quiz():
    try:
        words = read_words()
    except FileNotFoundError:
        return jsonify({"error": "word database not found"}), 500
    except sqlite3.Error:
        return jsonify({"error": "word database could not be read"}), 500

    translations = list({japanese for _, japanese in words})
    if len(translations) < 4 or not words:
        return jsonify({"error": "at least four word translations are required"}), 500

    english, answer = random.choice(words)
    choices = random.sample(
        [japanese for japanese in translations if japanese != answer],
        3,
    )
    choices.append(answer)
    random.shuffle(choices)
    return jsonify({"english": english, "choices": choices})


@app.post("/api/ans_quiz")
def ans_quiz():
    data = request.get_json(silent=True) or {}
    english = str(data.get("english", "")).strip()
    japanese = str(data.get("japanese", "")).strip()
    if not english or not japanese:
        return jsonify({"error": "english and japanese are required"}), 400
    if not WORD_DB.exists():
        return jsonify({"error": "word database not found"}), 500

    try:
        with sqlite3.connect(WORD_DB) as con:
            row = con.execute(
                "SELECT 1 FROM words WHERE english = ? AND japanese = ? LIMIT 1",
                (english, japanese),
            ).fetchone()
    except FileNotFoundError:
        return jsonify({"error": "word database not found"}), 500
    except sqlite3.Error:
        return jsonify({"error": "word database could not be read"}), 500

    return jsonify({"correct": row is not None})


@app.get("/api/words")
def get_words():
    try:
        words = read_words()
    except FileNotFoundError:
        return jsonify({"error": "word database not found"}), 500
    except sqlite3.Error:
        return jsonify({"error": "word database could not be read"}), 500

    return jsonify([
        {"english": english, "japanese": japanese}
        for english, japanese in words
    ])


@app.post("/api/words")
def add_word():
    data = request.get_json(silent=True) or {}
    english = str(data.get("english", "")).strip()
    japanese = str(data.get("japanese", "")).strip()
    if not english or not japanese:
        return jsonify({"error": "english and japanese are required"}), 400

    WORD_DB.parent.mkdir(exist_ok=True)
    try:
        with sqlite3.connect(WORD_DB) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS words ("
                "english TEXT NOT NULL, japanese TEXT NOT NULL)"
            )
            duplicate = con.execute(
                "SELECT 1 FROM words WHERE english = ? AND japanese = ? LIMIT 1",
                (english, japanese),
            ).fetchone()
            if duplicate is not None:
                return jsonify({"error": "word already exists"}), 409
            con.execute(
                "INSERT INTO words (english, japanese) VALUES (?, ?)",
                (english, japanese),
            )
    except sqlite3.Error:
        return jsonify({"error": "word database could not be updated"}), 500

    return jsonify({"english": english, "japanese": japanese}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
