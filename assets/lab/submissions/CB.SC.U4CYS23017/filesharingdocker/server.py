from flask import Flask, send_from_directory
import os

app = Flask(__name__)

UPLOAD_DIR = "uploads"

@app.route("/")
def home():
    files = [f for f in os.listdir(UPLOAD_DIR) if not f.startswith(".")]

    html = "<h2>Internal File Sharing Service - Version 2.0</h2>"
    html += f"<p><b>Available Documents:</b> {len(files)}</p>"
    for file in files:
        html += f'<li><a href="/files/{file}">{file}</a></li>'

    html += "</ul>"

    return html

@app.route("/files/<filename>")
def files(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
