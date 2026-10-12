import os
import socket
import json
import time


# Read configuration from environment variables
CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

HOST = "0.0.0.0"
PORT = 5001



def get_logical_clock():
    """
    Returns the current logical clock value.
    Uses the same Unix-time base as the master,
    plus the configured clock offset.
    """
    return time.time() + CLOCK_OFFSET


def apply_correction(correction):
    """
    Apply the correction received from the master.
    """
    global CLOCK_OFFSET

    CLOCK_OFFSET += correction


def handle_request(request):
    """
    Process a request received from the master.
    """

    if request.get("type") == "CLOCK_REQUEST":

        current_clock = get_logical_clock()

        return {
            "type": "CLOCK_RESPONSE",
            "client_id": CLIENT_ID,
            "clock": current_clock
        }

    elif request.get("type") == "CORRECTION":

        correction = float(request.get("correction", 0))

        old_clock = get_logical_clock()

        apply_correction(correction)

        new_clock = get_logical_clock()

        print(
            f"[{CLIENT_ID}] Correction received: "
            f"{correction:+.2f} sec"
        )

        print(
            f"[{CLIENT_ID}] Clock before correction: "
            f"{old_clock:.2f}"
        )

        print(
            f"[{CLIENT_ID}] Clock after correction: "
            f"{new_clock:.2f}"
        )

        return {
            "type": "CORRECTION_ACK",
            "client_id": CLIENT_ID,
            "clock": new_clock
        }

    return {
        "type": "ERROR",
        "message": "Unknown request"
    }


def start_server():
    """
    Start the client server and wait for requests
    from the master.
    """

    print("=" * 50)
    print(f"Starting {CLIENT_ID}")
    print(f"Initial Clock Offset: {CLOCK_OFFSET:+.2f} seconds")
    print(f"Initial Logical Clock: {get_logical_clock():.2f}")
    print("=" * 50)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[{CLIENT_ID}] Listening on port {PORT}...")

    while True:

        connection, address = server.accept()

        try:

            data = connection.recv(4096)

            if data:

                request = json.loads(data.decode())

                response = handle_request(request)

                connection.sendall(
                    json.dumps(response).encode()
                )

        except Exception as error:

            print(f"[{CLIENT_ID}] Error: {error}")

        finally:

            connection.close()


if __name__ == "__main__":
    start_server()