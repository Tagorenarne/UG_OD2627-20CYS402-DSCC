from flask import Flask, send_file
import json
import os

app = Flask(__name__)

with open("config.json", "r") as f:
    config = json.load(f)

@app.route("/")
def home():
    html = f"<h1>{config['application']}</h1><ul>"

    for path in config["files"]:
        name = os.path.basename(path)
        html += f'<li><a href="/file/{name}">{name}</a></li>'

    html += "</ul>"
    return html

@app.route("/file/<filename>")
def open_file(filename):
    for path in config["files"]:
        if os.path.basename(path) == filename:
            return send_file(path)

    return "File not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)