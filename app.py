from flask import Flask, render_template, request, redirect, session
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "clinic_secret_key"


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    if request.form["username"] == "admin" and request.form["password"] == "admin123":
        session["admin"] = True
        return redirect("/dashboard")
    return "Invalid Credentials"


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")
    return render_template("dashboard.html")


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (name, age, gender, contact) VALUES (%s,%s,%s,%s)",
            (
                request.form["name"],
                request.form["age"],
                request.form["gender"],
                request.form["contact"]
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/patients")

    return render_template("add_patient.html")


@app.route("/patients")
def patients():
    if "admin" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("patients.html", patients=data)


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if "admin" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute(
            "INSERT INTO appointments (patient_id, appointment_date, appointment_time) VALUES (%s,%s,%s)",
            (
                request.form["patient_id"],
                request.form["date"],
                request.form["time"]
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/dashboard")

    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("appointment.html", patients=patients)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
