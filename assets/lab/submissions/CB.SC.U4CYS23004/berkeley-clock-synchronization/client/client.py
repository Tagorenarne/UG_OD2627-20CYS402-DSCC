import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

MASTER_HOST = "clock-master"


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


def handle_request(conn):
    global CLOCK_OFFSET

    data = conn.recv(1024).decode().strip()

    if data == "CLOCK_REQUEST":

        current_clock = logical_time()

        print(
            f"[{CLIENT_ID}] CLOCK_REQUEST received"
        )

        print(
            f"[{CLIENT_ID}] Sending clock: "
            f"{format_time(current_clock)}"
        )

        conn.sendall(str(current_clock).encode())

    elif data.startswith("CORRECTION:"):

        correction = float(
            data.split(":", 1)[1]
        )

        before = logical_time()

        CLOCK_OFFSET += correction

        after = logical_time()

        print("\n" + "=" * 50)
        print(f"[{CLIENT_ID}] CORRECTION RECEIVED")
        print("=" * 50)

        print(
            f"Correction : {correction:+.2f} sec"
        )

        print(
            f"Before     : {format_time(before)}"
        )

        print(
            f"After      : {format_time(after)}"
        )

        conn.sendall(
            f"CORRECTED:{after}".encode()
        )


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen()

print("=" * 50)
print("       BERKELEY CLIENT")
print("=" * 50)

print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Offset  : {CLOCK_OFFSET:+.2f} sec")
print(
    f"Initial Clock   : "
    f"{format_time(logical_time())}"
)

print(f"Listening on    : {HOST}:{PORT}")
print("=" * 50)

while True:

    conn, address = server.accept()

    try:
        handle_request(conn)

    except Exception as e:

        print(
            f"[{CLIENT_ID}] Error: {e}"
        )

    finally:

        conn.close()