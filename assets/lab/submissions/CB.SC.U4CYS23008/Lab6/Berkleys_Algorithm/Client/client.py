import socket
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# Configuration
# ==========================================

MASTER_HOST = os.getenv("MASTER_HOST", "master")
MASTER_PORT = int(os.getenv("MASTER_PORT", "5000"))

CLIENT_ID = os.getenv("CLIENT_ID", "client1")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# Logical Clock
# ==========================================

def logical_clock():
    return time.time() + CLOCK_OFFSET


def format_clock(timestamp):
    return datetime.fromtimestamp(
        timestamp, IST
    ).strftime("%H:%M:%S.%f")[:-3]


def send_message(sock, message):
    sock.sendall((message + "\n").encode("utf-8"))


def receive_message(sock):
    buffer = ""

    while "\n" not in buffer:
        data = sock.recv(4096)

        if not data:
            raise ConnectionError("Master disconnected")

        buffer += data.decode("utf-8")

    message, _ = buffer.split("\n", 1)
    return message.strip()


# ==========================================
# Start Client
# ==========================================

print("=" * 50, flush=True)
print(f"{CLIENT_ID} started", flush=True)
print(f"Initial clock offset: {CLOCK_OFFSET:+.1f} seconds", flush=True)
print("Time Zone: IST (Asia/Kolkata)", flush=True)
print("=" * 50, flush=True)


# ==========================================
# Connect to Master
# ==========================================

sock = None

while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        print(
            f"{CLIENT_ID}: Connecting to {MASTER_HOST}:{MASTER_PORT}...",
            flush=True
        )

        sock.connect((MASTER_HOST, MASTER_PORT))
        sock.settimeout(None)

        send_message(sock, f"HELLO|{CLIENT_ID}")
        print(f"{CLIENT_ID}: Connected to master", flush=True)
        break

    except (OSError, socket.timeout) as e:
        print(f"{CLIENT_ID}: Connection failed: {e}. Retrying...", flush=True)

        if sock is not None:
            sock.close()

        time.sleep(2)


# ==========================================
# Handle Requests
# ==========================================

try:
    with sock:
        while True:
            message = receive_message(sock)

            if message == "CLOCK_REQUEST":
                current_clock = logical_clock()

                print(
                    f"{CLIENT_ID}: Clock request received",
                    flush=True
                )
                print(
                    f"{CLIENT_ID}: Current clock = "
                    f"{format_clock(current_clock)}",
                    flush=True
                )

                send_message(
                    sock,
                    f"CLOCK_RESPONSE|{CLIENT_ID}|{current_clock:.9f}"
                )

            elif message.startswith("CORRECTION|"):
                parts = message.split("|")

                if len(parts) != 2:
                    print("Invalid correction message", flush=True)
                    continue

                correction = float(parts[1])

                print(
                    f"{CLIENT_ID}: Correction received = "
                    f"{correction:+.3f} seconds",
                    flush=True
                )

                CLOCK_OFFSET += correction

                print(
                    f"{CLIENT_ID}: Corrected clock = "
                    f"{format_clock(logical_clock())}",
                    flush=True
                )
                print(
                    f"{CLIENT_ID}: Synchronization complete",
                    flush=True
                )

            else:
                print(f"{CLIENT_ID}: Unknown message: {message}", flush=True)

except (ConnectionError, OSError, ValueError) as e:
    print(f"{CLIENT_ID}: Communication error: {e}", flush=True)