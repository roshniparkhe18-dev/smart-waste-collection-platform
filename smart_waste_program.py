from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'waste.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            category TEXT NOT NULL,
            address TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            pickup_time TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/request-pickup", methods=["GET", "POST"])
def request_pickup():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        category = request.form["category"]
        address = request.form["address"]
        pickup_date = request.form["pickup_date"]
        pickup_time = request.form["pickup_time"]
        notes = request.form.get("notes", "")
        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO requests (name, phone, category, address, pickup_date, pickup_time, notes, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, category, address, pickup_date, pickup_time, notes, 'Pending', datetime.now().isoformat()))
        conn.commit()
        request_id = cursor.lastrowid
        conn.close()
        return redirect(f"/track?id={request_id}")
    else:
        categories = ["Organic", "Plastic", "Paper", "Glass", "Metal", "E-Waste", "Mixed Waste"]
        return render_template("request_pickup.html", categories=categories)

@app.route("/track")
def track():
    req_id = request.args.get("id")
    conn = get_db()
    req = None
    if req_id:
        req = conn.execute("SELECT * FROM requests WHERE id = ?", (req_id,)).fetchone()
    conn.close()
    return render_template("track.html", request_data=req, request_id=req_id)

if __name__ == "__main__":
    app.run(debug=True)
