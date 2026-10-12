import os
import socket
import threading
import time
from datetime import datetime

OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
DELAY = float(os.getenv("DELAY_MS", "0")) / 1000   # artificial network delay
PORT = 5000


def clock():
    return time.time() + OFFSET


def fmt(t):
    return datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def handle(conn, addr):
    request = conn.recv(1024).decode()

    time.sleep(DELAY / 2)          # delay on the way to the master
    master_time = clock()
    time.sleep(DELAY / 2)          # delay on the way back to the client

    conn.send(str(master_time).encode())
    conn.close()
    print(f"{request} from {addr[0]}  ->  MASTER_TIME = {fmt(master_time)}")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", PORT))
server.listen()

print(f"Time Server started on port {PORT}")
print(f"Artificial delay: {DELAY * 1000:.0f} ms")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle, args=(conn, addr)).start()
