import os
import socket
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(
    os.getenv("CLOCK_OFFSET", "0")
)

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

# Logical clock offset
logical_offset = CLOCK_OFFSET


def get_clock():
    """Return the current logical clock."""
    return time.time() + logical_offset


def main():
    global logical_offset

    print("=" * 50)
    print(f"Starting {CLIENT_ID}")
    print(
        f"Initial clock offset: "
        f"{logical_offset:+.2f} seconds"
    )
    print("=" * 50)

    while True:

        try:
            print(
                f"{CLIENT_ID}: "
                "Connecting to master..."
            )

            with socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            ) as sock:

                sock.connect(
                    (MASTER_HOST, MASTER_PORT)
                )

                # Get current logical clock
                current_clock = get_clock()

                # Send clock to master
                message = (
                    f"CLOCK|"
                    f"{CLIENT_ID}|"
                    f"{current_clock}"
                )

                sock.sendall(
                    message.encode()
                )

                print(
                    f"{CLIENT_ID}: "
                    f"Sent clock = "
                    f"{current_clock:.2f}"
                )

                # Receive correction
                response = sock.recv(
                    1024
                ).decode()

                if response.startswith(
                    "CORRECTION"
                ):

                    correction = float(
                        response.split("|")[1]
                    )

                    print(
                        f"{CLIENT_ID}: "
                        f"Received correction = "
                        f"{correction:+.2f} seconds"
                    )

                    # Apply Berkeley correction
                    logical_offset += correction

                    final_clock = get_clock()

                    print(
                        f"{CLIENT_ID}: "
                        f"Final clock = "
                        f"{final_clock:.2f}"
                    )

                    print("-" * 50)

                    break

        except ConnectionRefusedError:

            print(
                f"{CLIENT_ID}: "
                "Master not ready. "
                "Retrying in 2 seconds..."
            )

            time.sleep(2)

        except Exception as e:

            print(
                f"{CLIENT_ID}: "
                f"Error: {e}"
            )

            time.sleep(2)


if __name__ == "__main__":
    main()
