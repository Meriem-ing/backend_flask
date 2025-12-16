from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os

app = Flask(__name__)
CORS(app)
DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255),
            password_plain VARCHAR(255)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/register", methods=["POST"])
def register():
    if request.is_json:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

    if not email or not password:
        return jsonify({"message": "Champs manquants"}), 400

    password_hashed = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password, password_plain)
            VALUES (%s, %s, %s);
        """, (email, password_hashed, password))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Inscription réussie"})
    except Exception as e:
        return jsonify({"message": str(e)}), 400
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_conn()
        cur = conn.cursor()

        # 👇 récupérer email, password haché et password en clair
        cur.execute("""
            SELECT email, password, password_plain
            FROM users;
        """)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        users = []
        for row in rows:
            users.append({
                "email": row[0],
                "password": row[1],          # password haché
                "password_plain": row[2]     # password en clair
            })

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
