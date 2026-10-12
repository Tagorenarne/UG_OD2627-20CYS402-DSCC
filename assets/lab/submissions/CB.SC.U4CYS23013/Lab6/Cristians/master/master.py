"""
Cristian's Clock Synchronization Algorithm - Master / Time Server

Responsibilities:
1. Start a TCP server.
2. Listen for client TIME_REQUEST messages.
3. Maintain its own logical (reference) clock - i.e. real system time, offset = 0.
4. Return the current time to any client that asks.
5. Optionally introduce an artificial processing/network delay (ARTIFICIAL_DELAY env var).
6. Log every request it receives.
"""

import socket
import threading
import time
import os
import json
import datetime

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))

# Artificial delay (seconds) the master sleeps before replying.
# Lets us simulate different network / processing conditions (Part J).
ARTIFICIAL_DELAY = float(os.environ.get("ARTIFICIAL_DELAY", 0))


def now_str(ts=None):
    """Human readable HH:MM:SS.mmm timestamp."""
    if ts is None:
        ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]


def handle_client(conn: socket.socket, addr):
    try:
        data = conn.recv(1024).decode().strip()
        if not data:
            return

        print(f"[MASTER] Request received from {addr} : {data}")

        if data == "TIME_REQUEST":
            # Simulate network/processing delay if configured.
            if ARTIFICIAL_DELAY > 0:
                time.sleep(ARTIFICIAL_DELAY)

            master_time = time.time()
            response = {
                "master_time": master_time,
                "master_time_str": now_str(master_time),
            }
            conn.sendall(json.dumps(response).encode())
            print(f"[MASTER] Replied MASTER_TIME = {now_str(master_time)} "
                  f"(artificial delay = {ARTIFICIAL_DELAY * 1000:.0f} ms) -> {addr}")
        else:
            conn.sendall(json.dumps({"error": "unknown command"}).encode())
    except Exception as exc:
        print(f"[MASTER] Error handling {addr}: {exc}")
    finally:
        conn.close()


def main():
    print("========== CRISTIAN'S ALGORITHM - MASTER / TIME SERVER ==========")
    print(f"[MASTER] Starting on {HOST}:{PORT}")
    print(f"[MASTER] Artificial delay configured: {ARTIFICIAL_DELAY * 1000:.0f} ms")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(16)

    print(f"[MASTER] Listening for client requests...")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[MASTER] Shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
