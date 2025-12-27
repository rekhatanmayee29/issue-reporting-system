from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import uuid
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'artanmayee29@gmail.com'
app.config['MAIL_PASSWORD'] = 'ttqk qbuc towy nwbm'
# ----------------------------------------

mail = Mail(app)

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            ref_id TEXT,
            category TEXT,
            date TEXT,
            fname TEXT,
            lname TEXT,
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

# ---------- ROUTES ----------
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
    ref_id = "SC-" + str(uuid.uuid4())[:6]

    photo = request.files['photo']
    photo_name = ""
    if photo:
        photo_name = ref_id + "_" + photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_name))

    data = (
        ref_id,
        request.form['category'],
        request.form['date'],
        request.form['fname'],
        request.form['lname'],
        request.form['address'],
        request.form['city'],
        request.form['district'],
        request.form['state'],
        request.form['pincode'],
        request.form['mobile'],
        request.form['email'],
        request.form['description'],
        photo_name
    )

    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

    # Email
    msg = Message(
        subject="Complaint Registered Successfully",
        sender=app.config['MAIL_USERNAME'],
        recipients=[request.form['email']],
        body=f"""
Hello {request.form['fname']},

Your complaint has been successfully registered.

Reference ID: {ref_id}

Thank you for helping us improve the city.

Smart City Lab
"""
    )
    mail.send(msg)

    return redirect(url_for("success", ref_id=ref_id))

@app.route("/success")
def success():
    ref_id = request.args.get("ref_id")
    return render_template("success.html", ref_id=ref_id)

if __name__ == "__main__":
    app.run(debug=True)
