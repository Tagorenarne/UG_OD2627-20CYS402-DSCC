import os
import socket
import json
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

HOST = "0.0.0.0"
PORT = 5001

start_time = time.time()


def get_clock():
    elapsed = time.time() - start_time
    return elapsed + CLOCK_OFFSET


def handle_request(data):
    command = data.get("command")

    if command == "CLOCK_REQUEST":
        return {
            "client_id": CLIENT_ID,
            "clock": get_clock()
        }

    elif command == "CORRECTION":
        correction = float(data.get("correction", 0))
        current_clock = get_clock()

        global CLOCK_OFFSET
        CLOCK_OFFSET += correction

        new_clock = get_clock()

        return {
            "client_id": CLIENT_ID,
            "old_clock": current_clock,
            "correction": correction,
            "new_clock": new_clock
        }

    return {"error": "Unknown command"}


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print("=" * 50)
print(f"{CLIENT_ID} started")
print(f"Initial clock offset: {CLOCK_OFFSET:+.2f} seconds")
print("=" * 50)

while True:
    connection, address = server.accept()

    try:
        data = connection.recv(4096).decode()

        if data:
            request = json.loads(data)
            response = handle_request(request)

            connection.sendall(
                json.dumps(response).encode()
            )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        connection.close()