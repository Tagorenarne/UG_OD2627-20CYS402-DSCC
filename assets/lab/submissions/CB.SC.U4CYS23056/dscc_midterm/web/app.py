from flask import Flask, request
import mysql.connector
import subprocess
import time

app = Flask(__name__)

subprocess.run(["service", "mariadb", "start"])
time.sleep(3)

subprocess.run("mysql -u root < init.sql", shell=True)

@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        db = mysql.connector.connect(
            host="localhost",
            user="midterm_user",
            password="midterm_pass",
            database="midterm_db"
        )

        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (request.form["username"], request.form["password"])
        )

        message = "Login Successful!" if cursor.fetchone() else "Invalid Username or Password!"

        cursor.close()
        db.close()

    return f"""
    <h2>Login Page</h2>
    <form method="POST">
    Username: <input name="username"><br><br>
    Password: <input type="password" name="password"><br><br>
    <button>Login</button>
    </form>
    <h3>{message}</h3>
    """

app.run(host="0.0.0.0", port=5000)