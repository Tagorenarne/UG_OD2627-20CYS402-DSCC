import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
RESPONSE_DELAY = float(os.getenv("RESPONSE_DELAY", "0"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)

print("MASTER TIME SERVER ==========>>>")
print(f"Clock Offset   : {CLOCK_OFFSET:+.2f} seconds")
print(f"Response Delay : {RESPONSE_DELAY * 1000:.0f} ms")
print(f"Listening on   : {HOST}:{PORT}")
print()

while True:

    conn, addr = server.accept()

    print(f"Request received from {addr}")

    if RESPONSE_DELAY > 0:
        time.sleep(RESPONSE_DELAY)

    server_time = time.time() + CLOCK_OFFSET

    server_datetime = datetime.fromtimestamp(server_time)

    print(
        f"Master time: "
        f"{server_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}"
    )

    conn.send(str(server_time).encode())

    conn.close()
