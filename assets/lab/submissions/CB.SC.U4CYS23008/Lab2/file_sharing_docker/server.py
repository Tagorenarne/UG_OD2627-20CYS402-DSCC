import os
import json
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

APP_ENV = os.environ.get("APP_ENV", "development")
APP_PORT = int(os.environ.get("APP_PORT", 8000))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
app_config = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        app_config = json.load(f)


@app.route("/")
def home():
    files = sorted(os.listdir(UPLOAD_DIR))

    file_list_html = "".join(
        f'<li><a href="/files/{f}">{f}</a></li>' for f in files
    ) or "<li>No files available</li>"

    return f"""
    <html>
        <head><title>File Sharing Docker</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>Welcome to Filesharing Docker</h1>
            <p>Environment: {APP_ENV}</p>
            <h2>Available Files</h2>
            <ul>
                {file_list_html}
            </ul>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return jsonify(files=files)


@app.route("/files/<path:filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify(error="No file part in request"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No file selected"), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_DIR, filename))
    return jsonify(message=f"{filename} uploaded successfully"), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)