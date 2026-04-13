# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:15:47 2026

@author: ALBERTO
"""

# =========================
# STEP 1: INSTALL DEPENDENCIES
# =========================
# Run in terminal:
# pip install flask flask-cors qrcode

# =========================
# STEP 2: BACKEND (app.py)
# =========================

from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
from datetime import datetime

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
    data = request.json
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
        return jsonify({"a":0,"b":0,"total":0})

    return jsonify({
        "a": (a/total)*100,
        "b": (b/total)*100,
        "total": total,
        "winner": "Camilo Sánchez" if a>b else "Camilo Pardo"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)