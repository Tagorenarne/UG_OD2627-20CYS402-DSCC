from flask import Flask
import os
import json


with open("config.json", "r") as file:
    config = json.load(file)

file_bytes = os.path.getsize(os.path.join(os.getenv("UPLOAD_DIR", "uploads"), "img.png"))


app = Flask(__name__)


@app.route("/")
def home():
    return f"Hello, my name is {config['name']} and the size of the file you imported is {file_bytes} bytes"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", 5000)))
