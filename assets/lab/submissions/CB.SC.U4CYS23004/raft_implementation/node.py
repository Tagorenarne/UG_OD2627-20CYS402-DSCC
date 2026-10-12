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

NODE_ID = os.getenv("NODE_ID", "1")
PORT = int(os.getenv("PORT", "5000"))
PEERS = [p.strip() for p in os.getenv("PEERS", "").split(",") if p.strip()]

# Total cluster size including self
TOTAL_NODES = len(PEERS) + 1
MAJORITY = (TOTAL_NODES // 2) + 1

# ---------------- Raft State ----------------

state = "Follower"
current_term = 0
voted_for = None
leader = None
last_heartbeat = time.time()

lock = threading.Lock()


# ---------------- Helpers ----------------

def get_election_timeout():
    """Returns a random election timeout between 5 and 8 seconds."""
    return random.uniform(5.0, 8.0)


# ---------------- Core Raft Loops ----------------

def send_heartbeat():
    """Runs periodically while the node is a Leader."""
    global state, current_term, leader

    while True:
        with lock:
            if state != "Leader":
                break
            term = current_term

        for peer in PEERS:
            try:
                res = requests.post(
                    f"{peer}/heartbeat",
                    json={"leader": NODE_ID, "term": term},
                    timeout=1.5
                )
                if res.status_code == 200:
                    resp_data = res.json()
                    # If a peer has a higher term, step down immediately
                    with lock:
                        if resp_data.get("term", 0) > current_term:
                            current_term = resp_data["term"]
                            state = "Follower"
                            voted_for = None
                            leader = None
                            break
            except Exception:
                pass

        print(f"[Leader {NODE_ID}] Sent heartbeat (Term {term})", flush=True)
        time.sleep(2)


def election_loop():
    """Monitors heartbeat timeouts and triggers elections when necessary."""
    global state, current_term, voted_for, leader, last_heartbeat

    timeout = get_election_timeout()

    while True:
        time.sleep(0.5)

        with lock:
            # Leaders don't trigger elections
            if state == "Leader":
                continue

            # Check if the heartbeat timeout has elapsed
            if time.time() - last_heartbeat < timeout:
                continue

            # Reset timer & convert to Candidate
            timeout = get_election_timeout()
            state = "Candidate"
            current_term += 1
            voted_for = NODE_ID
            election_term = current_term
            last_heartbeat = time.time()

        print(f"\n[Node {NODE_ID}] Starting election for Term {election_term}...", flush=True)

        votes = 1  # Vote for self

        for peer in PEERS:
            try:
                res = requests.post(
                    f"{peer}/vote",
                    json={"term": election_term, "candidate": NODE_ID},
                    timeout=1.5
                )
                if res.status_code == 200 and res.json().get("vote"):
                    votes += 1
            except Exception:
                pass

        with lock:
            # Verify we are still in the same term and candidate state
            if state == "Candidate" and current_term == election_term:
                if votes >= MAJORITY:
                    state = "Leader"
                    leader = NODE_ID
                    print("\n====================================", flush=True)
                    print(f" NODE {NODE_ID} ELECTED LEADER (Term {election_term})")
                    print("====================================\n", flush=True)

                    # Start heartbeat background worker
                    threading.Thread(target=send_heartbeat, daemon=True).start()
                else:
                    # Election failed to reach majority; revert to Follower
                    state = "Follower"
                    voted_for = None


# ---------------- API Endpoints ----------------

@app.route("/heartbeat", methods=["POST"])
def receive_heartbeat():
    global state, leader, current_term, last_heartbeat, voted_for

    data = request.get_json(force=True)
    incoming_term = data.get("term", 0)
    incoming_leader = data.get("leader")

    with lock:
        if incoming_term >= current_term:
            current_term = incoming_term
            leader = incoming_leader
            state = "Follower"
            voted_for = None
            last_heartbeat = time.time()
            return jsonify({"status": "ok", "term": current_term})

        # Reject stale leader
        return jsonify({"status": "rejected", "term": current_term}), 400


@app.route("/vote", methods=["POST"])
def vote():
    global voted_for, current_term, leader, state, last_heartbeat

    data = request.get_json(force=True)
    candidate = data.get("candidate")
    term = data.get("term", 0)

    with lock:
        if term > current_term:
            current_term = term
            voted_for = None
            leader = None
            state = "Follower"

        if term == current_term and (voted_for is None or voted_for == candidate):
            voted_for = candidate
            last_heartbeat = time.time()
            print(f"[Node {NODE_ID}] Voted for Node {candidate} (Term {term})", flush=True)
            return jsonify({"vote": True, "term": current_term})

    return jsonify({"vote": False, "term": current_term})


@app.route("/status")
def status():
    with lock:
        return jsonify({
            "node": NODE_ID,
            "state": state,
            "leader": NODE_ID if state == "Leader" else leader,
            "term": current_term,
            "voted_for": voted_for
        })


@app.route("/")
def home():
    with lock:
        current_leader = NODE_ID if state == "Leader" else leader
        return f"""
        <h2>Raft Node {NODE_ID}</h2>
        <ul>
            <li><b>State:</b> {state}</li>
            <li><b>Leader:</b> {current_leader}</li>
            <li><b>Term:</b> {current_term}</li>
            <li><b>Voted For:</b> {voted_for}</li>
        </ul>
        """


# ---------------- Entrypoint ----------------

if __name__ == "__main__":
    print("\n==============================", flush=True)
    print(f" Starting Node {NODE_ID}", flush=True)
    print(f" Peers: {PEERS}", flush=True)
    print(f" Quorum Majority Needed: {MAJORITY}", flush=True)
    print("==============================\n", flush=True)

    threading.Thread(target=election_loop, daemon=True).start()

    app.run(host="0.0.0.0", port=PORT, threaded=True)