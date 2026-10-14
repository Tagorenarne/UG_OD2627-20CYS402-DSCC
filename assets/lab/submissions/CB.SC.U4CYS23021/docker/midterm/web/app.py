import os
import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
    <h1>Log in</h1>
    <form method="post">
        Username: <input name="username">
        <br><br>
        Password: <input name="password" type="password">
        <br><br>
        <button type="submit">login</button>
    </form>
    <p> {{ msg }} </p>
"""

def get_db():
    return psycopg2.connect(
        host=os.environ.get("host", "db"),
        dbname=os.environ.get("dbname", "midterm_db"),
        user=os.environ.get("username", "midterm_user"),
        password=os.environ.get("password", "midterm_password"),
    )


@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM users WHERE username = %s AND password = %s",
            (request.form["username"], request.form["password"]),
        )
        msg = "Login successful" if cur.fetchone() else "Invalid username or password"
        conn.close()
    return render_template_string(PAGE, msg=msg)


app.run(host="0.0.0.0", port=5000)
