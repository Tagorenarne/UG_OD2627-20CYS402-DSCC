from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "File Sharing Service Running",
        "environment": os.getenv("APP_ENV"),
        "port": os.getenv("APP_PORT"),
        "upload_directory": os.getenv("UPLOAD_DIR")
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)