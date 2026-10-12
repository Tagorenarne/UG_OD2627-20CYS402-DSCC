from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="db",
    user="midterm_user",
    password="midterm_pass",
    database="midterm_db"
)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():

    username = request.form["username"]
    password = request.form["password"]

    cursor = db.cursor()

    query = """
    SELECT * FROM users
    WHERE username=%s AND password=%s
    """

    cursor.execute(query,(username,password))

    user = cursor.fetchone()

    if user:
        return render_template("success.html",
                               user=username)

    return render_template("failed.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
