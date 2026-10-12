from flask import Flask, request
import mysql.connector

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        db = mysql.connector.connect(host="127.0.0.1",user="midterm_user",password="midterm_pass",database="midterm_db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username, password))
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            message = "Login successful!"
        else:
            message = "Invalid username or password!"

    return f"""
    
    <html>
    <head>
        <title>Web Authentication</title>
    </head>

    <body>

        <h1>Web server application</h1>

        <form method="POST">

            Username:
            <input type="text" name="username">

            <br><br>

            Password:
            <input type="password" name="password">

            <br><br>

            <input type="submit" value="Login">

        </form>

        <h3>{message}</h3>

    </body>
    </html>
    """


app.run(host="0.0.0.0", port=5000)
