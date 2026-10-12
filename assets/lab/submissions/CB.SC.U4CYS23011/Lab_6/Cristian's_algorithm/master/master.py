from flask import Flask
import time

app = Flask(__name__)

@app.route("/time")
def get_time():
    return {"server_time": time.time()}

app.run(host="0.0.0.0", port=5000)
