from flask import Flask, request
import psycopg2
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = psycopg2.connect(
            host="127.0.0.1",
            database="midterm_db",
            user="midterm_user",
            password="midterm_pass"
        )

        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        if cursor.fetchone():
            message = "Login Successful! Welcome, " + username
        else:
            message = "Invalid Username or Password!"

        cursor.close()
        db.close()

    return f"""
    <html>
    <head>
        <title>Web Authentication</title>

        <style>
            body {{
                font-family: Arial;
                margin: 40px;
            }}

            h1 {{
                color: #333;
            }}

            input {{
                padding: 5px;
                margin: 5px;
            }}

            button {{
                padding: 5px 12px;
            }}

            .message {{
                margin-top: 25px;
            }}

            .student {{
                margin-top: 25px;
                font-size: 14px;
                color: #555;
            }}
        </style>
    </head>

    <body>

        <h1>Web Authentication</h1>

        <form method="POST">

            Username:
            <input type="text" name="username" required>
            <br>

            Password:
            <input type="password" name="password" required>
            <br>

            <button type="submit">Login</button>

        </form>

        <h3 class="message">{message}</h3>

        <div class="student">
            Name: {os.environ.get("NAME")}<br>
            Roll No: {os.environ.get("ROLLNUMBER")}
        </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
