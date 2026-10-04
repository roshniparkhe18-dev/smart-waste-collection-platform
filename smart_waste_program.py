
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "waste.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_database():

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


# Home page
@app.route("/")
def home():

    categories = [
        "Organic",
        "Plastic",
        "Paper",
        "Glass",
        "Metal",
        "E-Waste",
        "Mixed Waste"
    ]

    return render_template(
        "index.html",
        categories=categories
    )


# Submit pickup request
@app.route("/request-pickup", methods=["POST"])
def request_pickup():

    name = request.form["name"]
    phone = request.form["phone"]
    category = request.form["category"]
    address = request.form["address"]
    pickup_date = request.form["pickup_date"]
    pickup_time = request.form["pickup_time"]
    notes = request.form["notes"]

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO requests
        (
            name,
            phone,
            category,
            address,
            pickup_date,
            pickup_time,
            notes,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        category,
        address,
        pickup_date,
        pickup_time,
        notes,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    request_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return redirect(
        url_for("track", request_id=request_id)
    )


# Track request
@app.route("/track")
def track():

    request_id = request.args.get("id")

    conn = get_db()

    result = conn.execute(
        "SELECT * FROM requests WHERE id = ?",
        (request_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "track.html",
        request=result
    )


# Admin dashboard
@app.route("/admin")
def admin():

    conn = get_db()

    requests = conn.execute(
        "SELECT * FROM requests ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        requests=requests
    )


# Update request status
@app.route(
    "/update-status/<int:request_id>",
    methods=["POST"]
)
def update_status(request_id):

    status = request.form["status"]

    conn = get_db()

    conn.execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (
        status,
        request_id
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin")
    )

 create_database()
# Start application
if __name__ == "__main__":

   

    app.run(
        debug=True,
        host="0.0.0.0",
        port=8080
    )
