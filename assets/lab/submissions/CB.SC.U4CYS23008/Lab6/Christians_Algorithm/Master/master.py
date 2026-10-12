import socket
import time
import os
from datetime import datetime


HOST = "0.0.0.0"
PORT = 5000

# Artificial delay in milliseconds
DELAY_MS = float(os.getenv("DELAY_MS", "0"))


def get_master_time():
    return time.time()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen(10)

print("=" * 60)
print("              CRISTIAN'S CLOCK SERVER")
print("=" * 60)
print(f"Server running on port : {PORT}")
print(f"Artificial delay       : {DELAY_MS} ms")
print("=" * 60)
print()

while True:

    connection, address = server.accept()

    try:

        request = connection.recv(1024).decode()

        print(f"Request received from : {address}")
        print(f"Request               : {request}")

        if request == "TIME_REQUEST":

            # Artificial delay
            if DELAY_MS > 0:
                time.sleep(DELAY_MS / 1000)

            # Get current leader time
            master_time = get_master_time()

            # Send leader time to follower
            response = str(master_time)

            connection.sendall(
                response.encode()
            )

            formatted_time = datetime.fromtimestamp(
                master_time
            ).strftime("%H:%M:%S.%f")[:-3]

            print(
                f"Leader Time           : {formatted_time}"
            )

            print()

    except Exception as e:

        print(f"Error handling client: {e}")

    finally:

        connection.close()