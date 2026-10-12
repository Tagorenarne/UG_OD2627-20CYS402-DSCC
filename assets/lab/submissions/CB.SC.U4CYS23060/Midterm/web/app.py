from flask import Flask, request
import mysql.connector
app = Flask(__name__)
def get_connection():
    return mysql.connector.connect(
        host="db",
        user="midterm_user",
        password="midterm_pass",
        database="midterm_db"
    )
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        return "Login successful" if user else "Invalid credentials"
    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <button type="submit">Login</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)