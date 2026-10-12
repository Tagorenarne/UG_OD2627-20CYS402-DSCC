import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5050

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
MASTER_DELAY = float(os.getenv("MASTER_DELAY", "0"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen(10)


print("CRISTIAN MASTER SERVER")
print(f"Listening on port : {PORT}")
print(f"Clock offset      : {CLOCK_OFFSET} seconds")
print(f"Artificial delay  : {MASTER_DELAY} seconds")


while True:

    conn, addr = server_socket.accept()

    try:
        request = conn.recv(1024).decode()

        if request == "TIME_REQUEST":

            print(f"\nRequest received from {addr}")

            # Artificial delay for experiments
            if MASTER_DELAY > 0:
                time.sleep(MASTER_DELAY)

            # Master's logical clock
            master_time = time.time() + CLOCK_OFFSET

            print(
                "Master logical time:",
                datetime.fromtimestamp(master_time)
            )

            # Send master time to client
            conn.send(str(master_time).encode())

    except Exception as e:
        print("Server error:", e)

    finally:
        conn.close()
