import socket
import threading
import time
import os
import datetime


HOST = "0.0.0.0"
PORT = 5000

# Optional artificial processing/network delay (seconds), configurable
# via env var so Part J's experiments can be run without editing code.
ARTIFICIAL_DELAY = float(os.environ.get("ARTIFICIAL_DELAY", "0"))


def get_master_time():
    """The master's own logical clock. For this lab the master is the
    reference point, so its logical time is simply its real-world time
    (offset 0)."""
    return datetime.datetime.now()


def handle_client(connection, address):

    try:
        request = connection.recv(1024).decode().strip()

        if not request:
            return

        print(f"[master] Request received from {address}: {request}")

        if request == "TIME_REQUEST":

            # Optional artificial delay to simulate slow networks/processing
            if ARTIFICIAL_DELAY > 0:
                time.sleep(ARTIFICIAL_DELAY)

            master_time = get_master_time()
            response = f"MASTER_TIME={master_time.isoformat()}"

            connection.send(response.encode())

            print(f"[master] Sent {response} to {address}")

        else:
            print(f"[master] Unknown request from {address}: {request}")

    finally:
        connection.close()


def start_master():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(20)

    print("========== CRISTIAN'S ALGORITHM — MASTER ==========")
    print(f"Master / Time Server listening on port {PORT}")
    if ARTIFICIAL_DELAY > 0:
        print(f"Artificial delay enabled: {ARTIFICIAL_DELAY * 1000:.0f} ms")
    print("=====================================================\n")

    while True:
        connection, address = s.accept()
        # Handle each client on its own thread so multiple clients
        # syncing at roughly the same time don't block each other.
        threading.Thread(
            target=handle_client, args=(connection, address), daemon=True
        ).start()


if __name__ == "__main__":
    start_master()