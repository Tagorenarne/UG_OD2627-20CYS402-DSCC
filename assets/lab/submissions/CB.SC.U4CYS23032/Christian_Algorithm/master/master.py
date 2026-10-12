import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

DELAY_MS = int(os.getenv("DELAY_MS", "0"))

def get_logical_time():
    return time.time()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(10)

print("====================================")
print("       CRISTIAN TIME MASTER")
print("====================================")
print(f"Server listening on port {PORT}")
print(f"Artificial delay: {DELAY_MS} ms")
print()

while True:
    conn, address = server.accept()

    request = conn.recv(1024).decode().strip()

    if request == "TIME_REQUEST":
        print(f"Request received from {address}")

        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000)

        master_time = get_logical_time()

        response = str(master_time)
        conn.sendall(response.encode())

        print(f"Master Time: {master_time:.6f}")
        print()

    conn.close()