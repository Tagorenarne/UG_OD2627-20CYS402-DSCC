import socket
import time
import os
from datetime import datetime, timezone, timedelta


HOST = "0.0.0.0"
PORT = 5000

# Artificial delay in milliseconds
DELAY_MS = int(os.getenv("DELAY_MS", "0"))

# Indian Standard Time (UTC +5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def logical_time():
    """
    Master logical clock.

    The master uses the container's system time
    as the reference clock.
    """
    return time.time()


def format_time(timestamp):
    """
    Convert Unix timestamp to IST
    and display milliseconds.
    """
    return datetime.fromtimestamp(
        timestamp, IST
    ).strftime("%H:%M:%S.%f")[:-3]


# --------------------------------------------------
# Create TCP server
# --------------------------------------------------

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

print("=" * 55)
print("          CRISTIAN'S ALGORITHM")
print("              TIME SERVER")
print("=" * 55)

print(f"Server Address  : {HOST}")
print(f"Server Port     : {PORT}")
print(f"Artificial Delay: {DELAY_MS} ms")
print("Time Zone       : IST (UTC+5:30)")
print()

# --------------------------------------------------
# Continuously accept client requests
# --------------------------------------------------

while True:

    conn, addr = server.accept()

    try:

        request = conn.recv(1024).decode().strip()

        print(
            f"[REQUEST] {addr[0]}:{addr[1]} "
            f"-> {request}"
        )

        if request == "TIME_REQUEST":

            # --------------------------------------------------
            # Artificial delay
            # --------------------------------------------------

            if DELAY_MS > 0:
                time.sleep(DELAY_MS / 1000)

            # --------------------------------------------------
            # Get master's current logical time
            # --------------------------------------------------

            master_time = logical_time()

            # Send timestamp to client
            response = str(master_time)

            conn.sendall(response.encode())

            print(
                f"[RESPONSE] Master Time: "
                f"{format_time(master_time)} IST"
            )

            print()

    except Exception as e:

        print(f"[ERROR] {e}")

    finally:

        conn.close()