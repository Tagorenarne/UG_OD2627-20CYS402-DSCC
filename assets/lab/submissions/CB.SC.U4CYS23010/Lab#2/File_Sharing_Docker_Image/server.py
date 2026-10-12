from flask import Flask, send_from_directory
import os

app = Flask(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")

@app.route("/")
def home():
    files = os.listdir(UPLOAD_DIR)
    html = "<h2>Available Files</h2><ul>"
    for file in files:
        html += f'<li><a href="/download/{file}">{file}</a></li>'
    html += "</ul>"
    return html

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 8000))
    app.run(host="0.0.0.0", port=port)
