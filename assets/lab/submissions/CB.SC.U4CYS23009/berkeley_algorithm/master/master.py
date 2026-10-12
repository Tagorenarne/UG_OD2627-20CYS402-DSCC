import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

DELAY = float(os.getenv("MASTER_DELAY", "0"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)

print("========================================")
print("       CRISTIAN'S CLOCK SERVER")
print("========================================")
print(f"Server listening on port {PORT}")
print(f"Artificial delay: {DELAY * 1000:.0f} ms")

while True:
    conn, addr = server.accept()

    print(f"Request received from {addr}")

    data = conn.recv(1024).decode()

    if data == "TIME_REQUEST":

        if DELAY > 0:
            time.sleep(DELAY)

        master_time = time.time()

        conn.send(str(master_time).encode())

        print(f"Sent master time: {master_time}")

    conn.close()