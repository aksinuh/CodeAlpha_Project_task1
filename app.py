from flask import Flask, request, redirect, jsonify
import sqlite3
import random
import string

app = Flask(__name__)

# ================== DATABASE INIT ====================
def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ================== SHORT CODE CREATOR ====================
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


# ================== SHORTEN URL ====================
@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_short_code()

    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
    conn.commit()
    conn.close()

    return jsonify({
        "original_url": original_url,
        "short_url": f"http://localhost:5000/{short_code}"
    })


# ================== REDIRECT ====================
@app.route("/<short_code>")
def redirect_to_original(short_code):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return redirect(row[0])
    else:
        return jsonify({"error": "Short URL not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
