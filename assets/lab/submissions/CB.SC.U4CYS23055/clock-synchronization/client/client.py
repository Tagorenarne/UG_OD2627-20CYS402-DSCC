import socket
import time
import os

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

start_time = time.time()

# Total correction accumulated by Berkeley synchronization
correction = 0.0


def get_logical_clock():
    return time.time() - start_time + CLOCK_OFFSET + correction


def format_clock(seconds):
    seconds = seconds % 86400

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:04.1f}"


def start_client():

    global correction

    print("======================================")
    print(f"        {CLIENT_ID.upper()}")
    print("======================================")

    print(f"Client ID     : {CLIENT_ID}")
    print(f"Initial Offset: {CLOCK_OFFSET:+.1f} seconds")

    while True:

        try:

            client_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            client_socket.connect(
                (MASTER_HOST, MASTER_PORT)
            )

            request = client_socket.recv(1024).decode()

            if request == "CLOCK_REQUEST":

                current_clock = get_logical_clock()

                message = f"{CLIENT_ID}|{current_clock}"

                client_socket.sendall(
                    message.encode()
                )

                # Wait for correction from master
                correction_message = client_socket.recv(1024).decode()

                if correction_message.startswith("CORRECTION|"):

                    new_correction = float(
                        correction_message.split("|")[1]
                    )

                    print("\n--------------------------------------")
                    print("BERKELEY SYNCHRONIZATION")
                    print("--------------------------------------")

                    print(
                        f"Clock before correction : "
                        f"{format_clock(current_clock)}"
                    )

                    print(
                        f"Correction received     : "
                        f"{new_correction:+.2f} seconds"
                    )

                    # Apply the new correction permanently
                    correction += new_correction

                    final_clock = get_logical_clock()

                    print(
                        f"Clock after correction  : "
                        f"{format_clock(final_clock)}"
                    )

            client_socket.close()

            time.sleep(3)

        except Exception as e:

            print(f"Waiting for master... ({e})")
            time.sleep(2)


if __name__ == "__main__":
    start_client()