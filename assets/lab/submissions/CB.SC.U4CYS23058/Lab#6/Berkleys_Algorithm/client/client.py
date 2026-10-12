import socket
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo


# ==========================================
# Configuration
# ==========================================

MASTER_HOST = os.getenv(
    "MASTER_HOST",
    "berkeley-master"
)

MASTER_PORT = int(
    os.getenv("MASTER_PORT", "5000")
)

CLIENT_ID = os.getenv(
    "CLIENT_ID",
    "client"
)

CLOCK_OFFSET = float(
    os.getenv("CLOCK_OFFSET", "0")
)

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# Logical Clock
# ==========================================

def logical_clock():
    """
    Current real time + configured logical offset.
    """

    return time.time() + CLOCK_OFFSET


# ==========================================
# Format Clock as IST
# ==========================================

def format_clock(timestamp):

    return datetime.fromtimestamp(
        timestamp,
        IST
    ).strftime("%H:%M:%S.%f")[:-3]


# ==========================================
# Start Client
# ==========================================

print("=" * 50)
print(f"{CLIENT_ID} started")
print(
    f"Initial clock offset: "
    f"{CLOCK_OFFSET:+.1f} seconds"
)
print("Time Zone: IST (Asia/Kolkata)")
print("=" * 50)


# ==========================================
# Connect to Master
# ==========================================

while True:

    try:

        print(
            f"{CLIENT_ID}: Connecting to "
            f"{MASTER_HOST}:{MASTER_PORT}..."
        )

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.connect(
            (MASTER_HOST, MASTER_PORT)
        )

        print(
            f"{CLIENT_ID}: Connected to master"
        )

        break

    except ConnectionRefusedError:

        print(
            f"{CLIENT_ID}: Master not ready. "
            "Retrying..."
        )

        time.sleep(2)


# ==========================================
# Listen for Master Requests
# ==========================================

while True:

    try:

        data = sock.recv(1024).decode().strip()

        if not data:

            print(
                f"{CLIENT_ID}: Master disconnected"
            )

            break


        # ==================================
        # Clock Request
        # ==================================

        if data == "CLOCK_REQUEST":

            current_clock = logical_clock()

            print(
                f"{CLIENT_ID}: Clock request received"
            )

            print(
                f"{CLIENT_ID}: Current clock = "
                f"{format_clock(current_clock)}"
            )

            response = (
                f"CLOCK_RESPONSE|"
                f"{CLIENT_ID}|"
                f"{current_clock}"
            )

            sock.sendall(
                response.encode()
            )


        # ==================================
        # Correction
        # ==================================

        elif data.startswith("CORRECTION"):

            parts = data.split("|")

            correction = float(parts[1])

            print(
                f"{CLIENT_ID}: Correction received = "
                f"{correction:+.3f}s"
            )

            CLOCK_OFFSET += correction

            print(
                f"{CLIENT_ID}: New clock = "
                f"{format_clock(logical_clock())}"
            )

            print(
                f"{CLIENT_ID}: "
                "Synchronization complete"
            )


    except Exception as e:

        print(
            f"{CLIENT_ID}: Error: {e}"
        )

        break


sock.close()