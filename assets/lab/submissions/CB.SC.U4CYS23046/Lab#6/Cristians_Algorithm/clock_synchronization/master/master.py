import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

DELAY = float(os.getenv("SERVER_DELAY", "0"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Master Time Server started...")
print("Listening on port 5000")

while True:
    conn, addr = server.accept()

    request = conn.recv(1024).decode()

    if request == "TIME_REQUEST":
        print(f"Request received from {addr}")

        if DELAY > 0:
            time.sleep(DELAY)

        master_time = time.time()

        conn.send(str(master_time).encode())

    conn.close()