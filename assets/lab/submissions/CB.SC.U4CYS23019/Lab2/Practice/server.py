from flask import Flask, send_from_directory
import os

app = Flask(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")

@app.route("/")
def index():
    files = os.listdir(UPLOAD_DIR)

    html = """
    <html>
    <head>
        <title>File Sharing Service</title>
    </head>
    <body>
        <h1>Available Files</h1>
    """

    for file in files:
        ext = file.lower().split('.')[-1]

        if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            html += f"""
            <div style="margin-bottom:20px">
                <h3>{file}</h3>
                <img src="/uploads/{file}" width="300">
            </div>
            """
        else:
            html += f'<p><a href="/uploads/{file}">{file}</a></p>'

    html += """
    </body>
    </html>
    """
    return html


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)