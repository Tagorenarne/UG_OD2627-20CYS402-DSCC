import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

DELAY = float(os.getenv("MASTER_DELAY", "0"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(10)

print("======================================")
print("       CRISTIAN TIME SERVER")
print("======================================")
print(f"Server listening on port {PORT}")
print(f"Artificial delay: {DELAY} seconds")
print()

while True:

    conn, addr = server.accept()

    print(f"Request received from {addr}")

    data = conn.recv(1024).decode()

    if data == "TIME_REQUEST":

        if DELAY > 0:
            time.sleep(DELAY)

        master_time = time.time()

        response = str(master_time)

        conn.sendall(response.encode())

        print(f"Master time sent: {master_time}")

    conn.close()