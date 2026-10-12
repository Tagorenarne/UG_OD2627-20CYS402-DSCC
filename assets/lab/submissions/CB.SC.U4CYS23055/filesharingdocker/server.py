from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return f"""
    <h2>File Sharing Service</h2>
    <p>Environment: {os.getenv('APP_ENV')}</p>
    <p>Port: {os.getenv('APP_PORT')}</p>
    <p>Upload Directory: {os.getenv('UPLOAD_DIR')}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", 8000)))