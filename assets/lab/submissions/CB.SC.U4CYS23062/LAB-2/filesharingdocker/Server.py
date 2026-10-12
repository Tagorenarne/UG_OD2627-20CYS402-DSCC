from flask import Flask
import json
import os

app = Flask(__name__)

# Read configuration from config.json
with open("config.json", "r") as file:
    config = json.load(file)

@app.route("/")
def home():
    files = os.listdir(config["upload_directory"])

    return f"""
    <h1>{config['app_name']}</h1>
    <h3>Version: {config['version']}</h3>
    <h3>Environment: {config['environment']}</h3>
    <h3>Files in Upload Directory:</h3>
    <ul>
        {''.join([f'<li>{file}</li>' for file in files])}
    </ul>
    """

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config["port"]
    )