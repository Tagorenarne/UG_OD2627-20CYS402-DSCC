from flask import Flask, render_template_string, abort
import os

app = Flask(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Home page - list all files
@app.route("/")
def home():
    if not os.path.exists(UPLOAD_DIR):
        return "Upload directory not found!"

    files = os.listdir(UPLOAD_DIR)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Internal File Sharing Service</title>
    </head>
    <body>
        <h1>Internal File Sharing Service</h1>
        <h3>Available Files</h3>
        <ul>
        {% for file in files %}
            <li><a href="/file/{{ file }}">{{ file }}</a></li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """

    return render_template_string(html, files=files)


# Display selected file
@app.route("/file/<filename>")
def show_file(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.isfile(filepath):
        abort(404)

    with open(filepath, "r") as f:
        content = f.read()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ filename }}</title>
    </head>
    <body>
        <h2>{{ filename }}</h2>

        <pre style="border:1px solid black;padding:10px;">
{{ content }}
        </pre>

        <br>

        <a href="/">⬅ Back to Files</a>

    </body>
    </html>
    """

    return render_template_string(html, filename=filename, content=content)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)