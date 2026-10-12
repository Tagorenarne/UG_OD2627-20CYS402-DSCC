from flask import Flask, send_from_directory, request
import os

app = Flask(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")

@app.route("/")
def home():
    return "Internal File Sharing Service is running!"

@app.route("/files")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@app.route("/files/<filename>")
def get_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 8000))
    app.run(host="0.0.0.0", port=port)
