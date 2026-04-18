# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# ---------- DATABASE ----------

def init_db():
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT,
            ip TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# 🔥 IMPORTANTE: crear DB al iniciar
init_db()

# ---------- HELPERS ----------

def get_client_ip(req):
    if req.headers.get('X-Forwarded-For'):
        return req.headers.get('X-Forwarded-For')
    return req.remote_addr

# ---------- ROUTES ----------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vote", methods=["POST"])
def vote():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    candidate = data.get("candidate")
    ip = get_client_ip(request)

    if candidate not in ["Camilo Sánchez", "Camilo Pardo"]:
        return jsonify({"error": "Invalid candidate"}), 400

    conn = sqlite3.connect("votes.db")
    c = conn.cursor()

    # Prevent multiple votes per IP
    c.execute("SELECT COUNT(*) FROM votes WHERE ip=?", (ip,))
    if c.fetchone()[0] > 0:
        conn.close()
        return jsonify({"error": "You have already voted"}), 403

    c.execute(
        "INSERT INTO votes (candidate, ip, timestamp) VALUES (?, ?, ?)",
        (candidate, ip, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    resp = make_response(jsonify({"message": "Vote recorded"}))
    resp.set_cookie("voted", "true", max_age=60*60*24*365)

    return resp

@app.route("/results")
def results():
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM votes WHERE candidate=?", ("Camilo Sánchez",))
    a = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM votes WHERE candidate=?", ("Camilo Pardo",))
    b = c.fetchone()[0]

    conn.close()

    total = a + b

    if total == 0:
        a_pct, b_pct = 0, 0
    else:
        a_pct = (a/total)*100
        b_pct = (b/total)*100

    return render_template(
        "results.html",
        a=a_pct,
        b=b_pct,
        total=total,
        winner="Camilo Sánchez" if a > b else "Camilo Pardo"
    )

# 🔥 IMPORTANTE: puerto dinámico para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)