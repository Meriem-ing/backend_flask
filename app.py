from flask import Flask, request, jsonify
import psycopg2
import hashlib
import os

app = Flask(__name__)

# URL de la base (Render la fournira dans les variables d’environnement)
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
            password VARCHAR(255)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"message": "Champs manquants"}), 400

    hashed = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password)
            VALUES (%s, %s);
        """, (email, hashed))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Inscription réussie"})
    except Exception as e:
        return jsonify({"message": str(e)}), 400

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
