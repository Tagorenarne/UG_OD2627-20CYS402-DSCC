import os
import mysql.connector
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details")

        rows = cursor.fetchall()

        conn.close()

        return f"Connected Successfully!<br>Total Records: {len(rows)}"

    except Exception as e:
        return f"Database Connection Failed<br><br>{e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)