import time
from flask import Flask, request, jsonify

from config import NODE_ID, PORT
from raft import raft_node
from node import State

app = Flask(__name__)


@app.route("/")
def home():
    return f"{NODE_ID} is running"


@app.route("/log")
def show_log():

    return jsonify({
        "node": NODE_ID,
        "state": raft_node.state.value,
        "term": raft_node.term,
        "log": raft_node.log
    })


@app.route("/client", methods=["POST"])
def client():

    if raft_node.state != State.LEADER:

        return jsonify({
            "success": False,
            "message": "Not Leader"
        })

    command = request.json["command"]

    success = raft_node.replicate_log(command)

    return jsonify({
        "success": success,
        "leader": NODE_ID
    })

@app.route("/append", methods=["POST"])
def append():

    data = request.json

    raft_node.last_heartbeat = time.time()

    if data["term"] > raft_node.term:
        raft_node.term = data["term"]

    raft_node.state = State.FOLLOWER

    entry = data.get("entry")

    if entry is not None:

        raft_node.log.append(entry)

        print(
            f"{NODE_ID} replicated: {entry}",
            flush=True
        )

    return jsonify({
        "success": True
    })


@app.route("/vote", methods=["POST"])
def vote():

    data = request.json

    candidate_term = data["term"]
    candidate = data["candidate"]

    if candidate_term < raft_node.term:

        return jsonify({
            "voteGranted": False,
            "term": raft_node.term
        })

    if candidate_term > raft_node.term:

        raft_node.term = candidate_term
        raft_node.voted_for = None
        raft_node.state = State.FOLLOWER

    if raft_node.voted_for is None:

        raft_node.voted_for = candidate

        print(
            f"{NODE_ID} voted for {candidate}",
            flush=True
        )

        return jsonify({
            "voteGranted": True,
            "term": raft_node.term
        })

    return jsonify({
        "voteGranted": False,
        "term": raft_node.term
    })


@app.route("/heartbeat", methods=["POST"])
def heartbeat():

    data = request.json

    raft_node.last_heartbeat = time.time()

    if data["term"] > raft_node.term:
        raft_node.term = data["term"]

    raft_node.state = State.FOLLOWER

    return jsonify({
        "success": True
    })


if __name__ == "__main__":

    print(
        f"Starting {NODE_ID} on port {PORT}",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=PORT
    )
