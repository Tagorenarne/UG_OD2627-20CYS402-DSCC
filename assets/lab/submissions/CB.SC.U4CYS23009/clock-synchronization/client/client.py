import os
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

def get_logical_time():
    return time.time() + CLOCK_OFFSET


@app.route("/clock", methods=["GET"])
def clock():
    return jsonify({
        "client_id": CLIENT_ID,
        "clock": get_logical_time()
    })


@app.route("/correct", methods=["POST"])
def correct():
    global CLOCK_OFFSET

    data = request.get_json()
    correction = float(data["correction"])

    CLOCK_OFFSET += correction

    return jsonify({
        "client_id": CLIENT_ID,
        "correction": correction,
        "new_clock": get_logical_time()
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "client_id": CLIENT_ID
    })


if __name__ == "__main__":
    print("=" * 50)
    print(f"{CLIENT_ID} started")
    print(f"Initial clock offset: {CLOCK_OFFSET:+.2f} seconds")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000
    )