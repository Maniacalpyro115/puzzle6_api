from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # allow GitHub Pages to call us

DB_PATH = "users.db"


def init_db():
    if os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)

    cur.executemany(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        [
            ("admin", "trustno1"),
            ("backup", "plaintext_is_bad"),
            ("service", "password123"),
        ]
    )

    conn.commit()
    conn.close()


@app.route("/login", methods=["POST"])
def login():
    init_db()

    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ⚠️ INTENTIONAL SQL INJECTION
    query = f"""
        SELECT * FROM users
        WHERE username = '{username}'
        AND password = '{password}'
    """

    try:
        cur.execute(query)
        row = cur.fetchone()
    except Exception as e:
        # INTENTIONAL ERROR LEAK (clue)
        return jsonify(error=str(e)), 500
    finally:
        conn.close()

    if row:
        return jsonify(message="Login successful. FLAG{sql_was_the_key}")
    else:
        return jsonify(message="Invalid credentials.")


@app.route("/")
def index():
    return jsonify(status="ok", database="sqlite")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
