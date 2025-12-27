from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import uuid
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "complaints.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE SETUP ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_id TEXT,
            category TEXT,
            report_date TEXT,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            city TEXT,
            district TEXT,
            state TEXT,
            pincode TEXT,
            mobile TEXT,
            email TEXT,
            description TEXT,
            photo TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/category")
def category():
    return render_template("category.html")


@app.route("/complaint")
def complaint():
    category = request.args.get("category")
    return render_template("complaint_form.html", category=category)


@app.route("/submit", methods=["POST"])
def submit():
    # Generate reference ID
    ref_id = "SC-" + uuid.uuid4().hex[:8].upper()

    # Safely get form values (NO KeyError)
    report_date = request.form.get("date")
    first_name = request.form.get("fname")
    last_name = request.form.get("lname")
    address = request.form.get("address")
    city = request.form.get("city")
    district = request.form.get("district")
    state = request.form.get("state")
    pincode = request.form.get("pincode")
    mobile = request.form.get("mobile")
    email = request.form.get("email")
    description = request.form.get("description")
    category = request.form.get("category")

    # Handle file upload
    photo_file = request.files.get("photo")
    photo_filename = None

    if photo_file and photo_file.filename != "":
        photo_filename = f"{ref_id}_{photo_file.filename}"
        photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

    # Insert into database (14 columns, 14 values)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (
            ref_id, category, report_date,
            first_name, last_name, address,
            city, district, state,
            pincode, mobile, email,
            description, photo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ref_id, category, report_date,
        first_name, last_name, address,
        city, district, state,
        pincode, mobile, email,
        description, photo_filename
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("success", ref_id=ref_id))


@app.route("/success")
def success():
    ref_id = request.args.get("ref_id")
    return render_template("success.html", ref_id=ref_id)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
