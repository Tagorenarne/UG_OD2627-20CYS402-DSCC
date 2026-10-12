import os
import json
from flask import Flask, jsonify

app = Flask(__revanth__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
APP_ENV = os.environ.get("APP_ENV", "development")

@app.route("/")
def home():
    return f"Welcome to the Internal File Sharing Service! (env: {APP_ENV})"

@app.route("/files")
def list_files():
    if not os.path.exists(UPLOAD_DIR):
        return jsonify({"files": [], "message": "Upload directory not found"})
    files = os.listdir(UPLOAD_DIR)
    return jsonify({"files": files})

if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 8000))
    app.run(host="0.0.0.0", port=port)