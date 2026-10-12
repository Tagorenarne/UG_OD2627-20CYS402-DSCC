import os
import socket
import time
from datetime import datetime

CLIENT_ID = os.getenv("CLIENT_ID", "client")
offset = float(os.getenv("CLOCK_OFFSET", "0"))
PORT = 5000


def clock():
    return time.time() + offset


def fmt(t):
    return datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", PORT))
server.listen()

print(f"[{CLIENT_ID}] started with offset {offset:+} sec | Clock: {fmt(clock())}")

while True:
    conn, _ = server.accept()
    message = conn.recv(1024).decode()

    if message == "CLOCK_REQUEST":
        conn.send(str(clock()).encode())

    elif message.startswith("CORRECTION"):
        correction = float(message.split()[1])
        before = clock()
        offset += correction
        after = clock()
        print(f"[{CLIENT_ID}] Before: {fmt(before)} | Correction: {correction:+.3f} sec | After: {fmt(after)}")
        conn.send(b"OK")

    conn.close()
