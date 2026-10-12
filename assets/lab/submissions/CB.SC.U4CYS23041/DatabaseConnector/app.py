from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

@app.route("/")
def home():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()

        # Fetch data from the table
        cursor.execute("SELECT * FROM employeese")
        rows = cursor.fetchall()

        html = """
        <html>
        <head>
            <title>Database Connector</title>
        </head>
        <body style="font-family: Arial; margin:40px;">
            <h1>Database Connected Successfully ✅</h1>

            <h3>Employee Details</h3>

            <table border="1" cellpadding="10" cellspacing="0">
                <tr style="background-color:#dddddd;">
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                </tr>
        """

        for row in rows:
            html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        cursor.close()
        conn.close()

        return html

    except Exception as e:
        return f"""
        <h2>Database Connection Failed ❌</h2>
        <pre>{e}</pre>
        """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
