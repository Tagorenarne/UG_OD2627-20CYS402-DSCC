import socket
import os
import time
from datetime import datetime


CLIENT_ID = os.getenv("CLIENT_ID", "client")
INITIAL_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

MASTER_HOST = "clock-master"
MASTER_PORT = 5000


def get_logical_time(offset):
    return time.time() + offset


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


def main():

    current_offset = INITIAL_OFFSET

    print("=" * 50)
    print("       BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 50)

    print(f"Client ID       : {CLIENT_ID}")
    print(f"Initial Offset  : {INITIAL_OFFSET:+.1f} seconds")

    print(
        f"Initial Clock   : "
        f"{format_time(get_logical_time(current_offset))}"
    )

    print()

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.connect(
            (MASTER_HOST, MASTER_PORT)
        )

        # ------------------------------------------
        # STEP 1: Send initial clock
        # ------------------------------------------

        initial_time = get_logical_time(
            current_offset
        )

        message = (
            f"CLOCK_REQUEST|"
            f"{CLIENT_ID}|"
            f"{initial_time}"
        )

        sock.sendall(message.encode())

        # ------------------------------------------
        # STEP 2: Receive correction
        # ------------------------------------------

        response = sock.recv(1024).decode()

        if response.startswith("CORRECTION"):

            correction = float(
                response.split("|")[1]
            )

            print("------------------------------------------")

            print(
                f"Correction Received : "
                f"{correction:+.3f} seconds"
            )

            # Apply Berkeley correction
            current_offset += correction

            print(
                f"Final Offset       : "
                f"{current_offset:+.3f} seconds"
            )

            # Small delay so the corrected logical
            # clock can be measured.
            time.sleep(0.1)

            final_time = get_logical_time(
                current_offset
            )

            print(
                f"Final Clock        : "
                f"{format_time(final_time)}"
            )

            # --------------------------------------
            # STEP 3: Send final clock
            # --------------------------------------

            final_message = (
                f"FINAL|"
                f"{CLIENT_ID}|"
                f"{final_time}"
            )

            sock.sendall(
                final_message.encode()
            )

            # Wait for master acknowledgement
            acknowledgement = sock.recv(1024).decode()

            if acknowledgement == "ACK":
                print(
                    "Final clock accepted by master."
                )

        sock.close()

    except Exception as e:

        print(f"Client error: {e}")


if __name__ == "__main__":
    main()