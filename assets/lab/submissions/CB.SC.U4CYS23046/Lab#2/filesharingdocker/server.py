# from flask import Flask, render_template_string, abort
# import json
# import os

# app = Flask(__name__)

# # Environment variables
# APP_ENV = os.getenv("APP_ENV", "production")
# APP_PORT = int(os.getenv("APP_PORT", 8000))

# # Read config.json
# with open("config.json", "r") as f:
#     config = json.load(f)

# APP_NAME = config.get("application_name", "File Sharing")
# SHARED_FOLDER = config.get("shared_folder", "uploads")


# @app.route("/")
# def home():

#     if not os.path.exists(SHARED_FOLDER):
#         return f"Folder '{SHARED_FOLDER}' does not exist."

#     files = sorted(os.listdir(SHARED_FOLDER))

#     html = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>{{app_name}}</title>
#         <style>
#             body{
#                 font-family: Arial;
#                 margin:40px;
#             }
#             h1{
#                 color:#1f4e79;
#             }
#             ul{
#                 list-style:none;
#                 padding:0;
#             }
#             li{
#                 margin:10px 0;
#             }
#             a{
#                 text-decoration:none;
#                 color:blue;
#             }
#         </style>
#     </head>

#     <body>

#     <h1>{{app_name}}</h1>

#     <p><b>Environment:</b> {{env}}</p>

#     <p><b>Shared Folder:</b> {{folder}}</p>

#     <hr>

#     <h2>Available Files</h2>

#     <ul>

#     {% for file in files %}
#         <li>
#             <a href="/view/{{file}}">
#                 {{file}}
#             </a>
#         </li>
#     {% endfor %}

#     </ul>

#     </body>
#     </html>
#     """

#     return render_template_string(
#         html,
#         app_name=APP_NAME,
#         env=APP_ENV,
#         folder=SHARED_FOLDER,
#         files=files
#     )


# @app.route("/view/<filename>")
# def view_file(filename):

#     filepath = os.path.join(SHARED_FOLDER, filename)

#     if not os.path.isfile(filepath):
#         abort(404)

#     with open(filepath, "r", encoding="utf-8") as f:
#         content = f.read()

#     html = """
#     <!DOCTYPE html>
#     <html>

#     <head>

#         <title>{{filename}}</title>

#         <style>

#             body{
#                 font-family:Arial;
#                 margin:40px;
#             }

#             pre{
#                 background:#f4f4f4;
#                 padding:20px;
#                 border-radius:5px;
#                 white-space:pre-wrap;
#             }

#             a{
#                 text-decoration:none;
#                 color:blue;
#             }

#         </style>

#     </head>

#     <body>

#     <h1>{{filename}}</h1>

#     <pre>{{content}}</pre>

#     <br>

#     <a href="/">← Back to Home</a>

#     </body>

#     </html>
#     """

#     return render_template_string(
#         html,
#         filename=filename,
#         content=content
#     )


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=APP_PORT)


from flask import Flask, render_template_string, abort, send_from_directory
import json
import os
import mimetypes

app = Flask(__name__)

# Environment variables
APP_ENV = os.getenv("APP_ENV", "production")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Read configuration
with open("config.json", "r") as f:
    config = json.load(f)

APP_NAME = config.get("application_name", "File Sharing")
SHARED_FOLDER = config.get("shared_folder", "uploads")


@app.route("/")
def home():

    if not os.path.exists(SHARED_FOLDER):
        return f"Folder '{SHARED_FOLDER}' does not exist."

    files = sorted(os.listdir(SHARED_FOLDER))

    html = """
    <!DOCTYPE html>
    <html>

    <head>
        <title>{{app_name}}</title>

        <style>

            body{
                font-family:Arial;
                margin:40px;
                background:#f5f5f5;
            }

            h1{
                color:#1f4e79;
            }

            ul{
                list-style:none;
                padding:0;
            }

            li{
                background:white;
                margin:10px 0;
                padding:12px;
                border-radius:6px;
                box-shadow:0 1px 3px rgba(0,0,0,0.2);
            }

            a{
                text-decoration:none;
                color:#0066cc;
                font-weight:bold;
            }

        </style>

    </head>

    <body>

        <h1>{{app_name}}</h1>

        <p><strong>Environment:</strong> {{env}}</p>
        <p><strong>Shared Folder:</strong> {{folder}}</p>

        <hr>

        <h2>Available Files</h2>

        <ul>

        {% for file in files %}

            <li>
                <a href="/view/{{file}}">
                    {{file}}
                </a>
            </li>

        {% endfor %}

        </ul>

    </body>

    </html>
    """

    return render_template_string(
        html,
        app_name=APP_NAME,
        env=APP_ENV,
        folder=SHARED_FOLDER,
        files=files
    )


@app.route("/view/<path:filename>")
def view_file(filename):

    filepath = os.path.join(SHARED_FOLDER, filename)

    if not os.path.isfile(filepath):
        abort(404)

    mime_type, _ = mimetypes.guess_type(filepath)

    # -------- TEXT FILES --------

    if mime_type and mime_type.startswith("text"):

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return render_template_string("""

        <html>

        <head>

        <title>{{filename}}</title>

        <style>

        body{
            font-family:Arial;
            margin:40px;
            background:#f5f5f5;
        }

        pre{
            background:white;
            padding:20px;
            border-radius:8px;
            white-space:pre-wrap;
            box-shadow:0 1px 3px rgba(0,0,0,0.2);
        }

        a{
            text-decoration:none;
        }

        </style>

        </head>

        <body>

        <h2>{{filename}}</h2>

        <pre>{{content}}</pre>

        <br>

        <a href="/">← Back</a>

        </body>

        </html>

        """, filename=filename, content=content)

    # -------- IMAGE FILES --------

    elif mime_type and mime_type.startswith("image"):

        return render_template_string("""

        <html>

        <head>

        <title>{{filename}}</title>

        <style>

        body{
            font-family:Arial;
            margin:40px;
            background:#f5f5f5;
            text-align:center;
        }

        img{
            max-width:90%;
            max-height:700px;
            border-radius:8px;
            box-shadow:0 2px 5px rgba(0,0,0,0.3);
        }

        a{
            text-decoration:none;
        }

        </style>

        </head>

        <body>

        <h2>{{filename}}</h2>

        <img src="/file/{{filename}}">

        <br><br>

        <a href="/">← Back</a>

        </body>

        </html>

        """, filename=filename)

    # -------- PDF --------

    elif mime_type == "application/pdf":

        return render_template_string("""

        <html>

        <head>

        <title>{{filename}}</title>

        <style>

        body{
            margin:20px;
            font-family:Arial;
        }

        embed{
            border:1px solid gray;
        }

        </style>

        </head>

        <body>

        <h2>{{filename}}</h2>

        <embed src="/file/{{filename}}" width="100%" height="700px">

        <br><br>

        <a href="/">← Back</a>

        </body>

        </html>

        """, filename=filename)

    # -------- OTHER FILE TYPES --------

    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)


@app.route("/file/<path:filename>")
def serve_file(filename):
    return send_from_directory(SHARED_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)