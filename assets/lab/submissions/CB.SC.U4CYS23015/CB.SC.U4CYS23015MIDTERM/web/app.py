import os
import mysql.connector
from flask import Flask, request, render_template

app = Flask(__name__)

rollnumber = os.environ.get("ROLLNUMBER", "N/A")
name = os.environ.get("NAME", "N/A")


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="midterm_user",
        password="midterm_pass",
        database="midterm_db"
    )


@app.route("/")
def index():
    return render_template("login.html", rollnumber=rollnumber, name=name)


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        return render_template("result.html", success=True,
                               message="Login successful. Welcome " + username + "!")
    else:
        return render_template("result.html", success=False,
                               message="Login failed. Wrong username or password.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
