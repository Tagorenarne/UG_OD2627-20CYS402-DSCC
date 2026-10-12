import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

ARTIFICIAL_DELAY = float(os.getenv("ARTIFICIAL_DELAY", "0"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Time Server running on port {PORT}")

while True:
    conn, addr = server.accept()

    data = conn.recv(1024).decode()

    print(f"Request received: {data}")

    time.sleep(ARTIFICIAL_DELAY)

    current_time = time.time()

    conn.send(str(current_time).encode())

    conn.close()
