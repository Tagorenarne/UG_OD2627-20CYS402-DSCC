from flask import Flask, request
import mysql.connector

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = mysql.connector.connect(
            host="localhost",
            user="midterm_user",
            password="midterm_pass",
            database="midterm_db"
        )

        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        result = cursor.fetchone()

        if result:
            message = "Login successful!"
        else:
            message = "Invalid username or password!"

        cursor.close()
        db.close()

    return """
    <h1>Midterm Web Authentication</h1>

    <form method="POST">

    Username:
    <input type="text" name="username">
    <br><br>

    Password:
    <input type="password" name="password">
    <br><br>

    <input type="submit" value="Login">

    </form>

    <h3>{}</h3>

    """.format(message)


app.run(host="0.0.0.0", port=5000)