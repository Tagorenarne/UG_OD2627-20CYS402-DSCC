from flask import Flask, send_file
import json
import os

app = Flask(__name__)

# Read environment variables set by your Dockerfile
PORT = int(os.environ.get("APP_PORT", 8000))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")

with open("config.json", "r") as f:
    config = json.load(f)

@app.route("/")
def home():
    html = f"<h1>{config['app_name']}</h1><ul>"

    # Dynamically read whatever files are inside your Docker uploads folder
    for name in os.listdir(UPLOAD_DIR):
        html += f'<li><a href="/file/{name}">{name}</a></li>'

    html += "</ul>"
    return html

@app.route("/file/<filename>")
def open_file(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return "File not found", 404

if __name__ == "__main__":
    # Uses the PORT from your Dockerfile environment variable
    app.run(host="0.0.0.0", port=PORT)