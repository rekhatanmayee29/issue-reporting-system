import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

# ---------------- APP SETUP ----------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "complaints.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- EMAIL CONFIG ----------------
# ⚠️ IMPORTANT:
# Use Gmail APP PASSWORD (not normal password)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "your_email@gmail.com"        # 🔴 CHANGE
app.config["MAIL_PASSWORD"] = "your_app_password_here"      # 🔴 CHANGE
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            main_category TEXT,
            sub_category TEXT,
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
def category_page():
    return render_template("category.html")


@app.route("/complaint")
def complaint_form():
    main_category = request.args.get("category")
    sub_category = request.args.get("issue")
    return render_template(
        "complaint_form.html",
        main_category=main_category,
        sub_category=sub_category
    )


@app.route("/submit", methods=["POST"])
def submit():
    ref_id = "SC-" + uuid.uuid4().hex[:8]

    # -------- PHOTO UPLOAD --------
    photo_file = request.files.get("photo")
    photo_name = None

    if photo_file and photo_file.filename:
        photo_name = f"{ref_id}_{photo_file.filename}"
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_name)
        photo_file.save(photo_path)

    # -------- FORM DATA --------
    data = (
        ref_id,
        request.form.get("main_category"),
        request.form.get("sub_category"),
        request.form.get("report_date"),
        request.form.get("fname"),
        request.form.get("lname"),
        request.form.get("address"),
        request.form.get("city"),
        request.form.get("district"),
        request.form.get("state"),
        request.form.get("pincode"),
        request.form.get("mobile"),
        request.form.get("email"),
        request.form.get("description"),
        photo_name
    )

    # -------- DATABASE INSERT --------
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    # -------- EMAIL CONFIRMATION --------
    try:
        msg = Message(
            subject="Smart City Complaint Registered",
            recipients=[request.form.get("email")],
            body=f"""
Hello {request.form.get("fname")},

Your complaint has been successfully registered.

Reference ID: {ref_id}

Category: {request.form.get("main_category")}
Issue Type: {request.form.get("sub_category")}

We will take necessary action shortly.

Thank you,
Smart City Lab
"""
        )
        mail.send(msg)
    except Exception as e:
        print("Email not sent:", e)

    return redirect(url_for("success", ref_id=ref_id))


@app.route("/success")
def success():
    ref_id = request.args.get("ref_id")
    return render_template("success.html", ref_id=ref_id)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
