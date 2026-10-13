import os
import time
import random
import threading
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hide Flask request logs
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# ---------------- Configuration ----------------

NODE_ID = os.getenv("NODE_ID")
PORT = int(os.getenv("PORT", "5000"))
PEERS = [p for p in os.getenv("PEERS", "").split(",") if p]

# ---------------- Raft State ----------------

state = "Follower"
current_term = 0
voted_for = None
leader = None
last_heartbeat = time.time()

lock = threading.Lock()


# ------------------------------------------------

def election_timeout():
    return random.uniform(5, 8)


# ------------------------------------------------

def heartbeat():
    global leader

    while True:

        with lock:

            if state != "Leader":
                break

            leader = NODE_ID
            term = current_term

        for peer in PEERS:

            try:
                requests.post(
                    peer + "/heartbeat",
                    json={
                        "leader": NODE_ID,
                        "term": term
                    },
                    timeout=2
                )
            except Exception:
                pass

        print(f"[Leader {NODE_ID}] Heartbeat sent (Term {term})", flush=True)

        time.sleep(2)


# ------------------------------------------------

def election():

    global state
    global current_term
    global voted_for
    global leader
    global last_heartbeat

    timeout = election_timeout()

    while True:

        time.sleep(1)

        with lock:

            if state == "Leader":
                continue

            if time.time() - last_heartbeat < timeout:
                continue

            timeout = election_timeout()

            state = "Candidate"
            current_term += 1
            voted_for = NODE_ID

            election_term = current_term

        print(
            f"\nNode {NODE_ID} started election (Term {election_term})",
            flush=True
        )

        votes = 1

        for peer in PEERS:

            try:

                response = requests.post(
                    peer + "/vote",
                    json={
                        "term": election_term,
                        "candidate": NODE_ID
                    },
                    timeout=2
                )

                if response.json()["vote"]:

                    votes += 1

            except Exception:
                pass

        majority = len(PEERS) // 2 + 1

        if votes >= majority:

            with lock:

                state = "Leader"
                leader = NODE_ID
                voted_for = NODE_ID
                last_heartbeat = time.time()

            print("\n====================================", flush=True)
            print(f"NODE {NODE_ID} BECAME LEADER", flush=True)
            print(f"TERM : {election_term}", flush=True)
            print("====================================\n", flush=True)

            threading.Thread(
                target=heartbeat,
                daemon=True
            ).start()

        else:

            with lock:

                state = "Follower"
                voted_for = None


# ------------------------------------------------

@app.route("/heartbeat", methods=["POST"])
def receive_heartbeat():

    global state
    global leader
    global current_term
    global last_heartbeat

    data = request.json

    with lock:

        if data["term"] >= current_term:

            current_term = data["term"]
            leader = data["leader"]
            state = "Follower"
            last_heartbeat = time.time()

    print(
        f"Node {NODE_ID} received heartbeat from Leader {leader}",
        flush=True
    )

    return jsonify({"status": "ok"})


# ------------------------------------------------

@app.route("/vote", methods=["POST"])
def vote():

    global voted_for
    global current_term
    global leader
    global state
    global last_heartbeat

    data = request.json

    candidate = data["candidate"]
    term = data["term"]

    with lock:

        if term > current_term:

            current_term = term
            voted_for = None
            leader = None
            state = "Follower"

        if term == current_term and (
                voted_for is None or voted_for == candidate):

            voted_for = candidate
            last_heartbeat = time.time()

            print(
                f"Node {NODE_ID} voted for Node {candidate} "
                f"(Term {term})",
                flush=True
            )

            return jsonify({"vote": True})

    return jsonify({"vote": False})


# ------------------------------------------------

@app.route("/status")
def status():

    with lock:

        current_state = state

        if current_state == "Leader":
            current_leader = NODE_ID
        else:
            current_leader = leader

        return jsonify({
            "node": NODE_ID,
            "state": current_state,
            "leader": current_leader,
            "term": current_term,
            "voted_for": voted_for
        })


# ------------------------------------------------

@app.route("/")
def home():

    with lock:

        if state == "Leader":
            current_leader = NODE_ID
        else:
            current_leader = leader

        return f"""
        <h2>Raft Node {NODE_ID}</h2>

        <ul>
            <li>State : {state}</li>
            <li>Leader : {current_leader}</li>
            <li>Term : {current_term}</li>
            <li>Voted For : {voted_for}</li>
        </ul>
        """


# ------------------------------------------------

if __name__ == "__main__":

    print("\n==============================", flush=True)
    print(f"Starting Node {NODE_ID}", flush=True)
    print(f"Peers : {PEERS}", flush=True)
    print("==============================\n", flush=True)

    threading.Thread(
        target=election,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )