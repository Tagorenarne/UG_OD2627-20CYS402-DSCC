import os
from flask import Flask, send_from_directory, render_template_string, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load configuration from environment variables
APP_ENV = os.environ.get("APP_ENV", "development")
APP_PORT = int(os.environ.get("APP_PORT", 8000))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")

# Security: Define allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md'}

# Ensure the upload directory exists to prevent crash on first upload
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Updated HTML template with an upload form and image previews
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Internal File Sharing</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9;}
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        li { margin: 15px 0; list-style-type: none; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        a { text-decoration: none; color: #007bff; font-weight: bold; font-size: 1.1em; }
        a:hover { text-decoration: underline; }
        .upload-section { background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .image-preview { max-width: 250px; max-height: 250px; display: block; margin-top: 10px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        button { background-color: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📁 Internal File Sharing Service</h2>
        <p><strong>Status:</strong> Running in {{ env }} mode</p>
        
        <div class="upload-section">
            <h3>Upload a New File</h3>
            <form action="/" method="POST" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <button type="submit">Upload File</button>
            </form>
        </div>
        
        <hr>
        <h3>Available Files:</h3>
        <ul>
            {% if files %}
                {% for file in files %}
                    <li>
                        <a href="/download/{{ file }}">{{ file }}</a>
                        {% if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) %}
                            <img src="/download/{{ file }}" class="image-preview" alt="{{ file }}">
                        {% endif %}
                    </li>
                {% endfor %}
            {% else %}
                <p>No files found in the upload directory.</p>
            {% endif %}
        </ul>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    # Handle the file upload if the method is POST
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # SECURITY: Sanitize the filename before saving to the filesystem
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, filename))
            return redirect(url_for('index'))

    # Handle the GET request to display files
    try:
        files = os.listdir(UPLOAD_DIR)
    except FileNotFoundError:
        files = []
    
    return render_template_string(HTML_TEMPLATE, files=files, env=APP_ENV)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
