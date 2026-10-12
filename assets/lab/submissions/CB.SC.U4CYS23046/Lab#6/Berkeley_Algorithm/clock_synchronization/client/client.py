import socket
import time
import os

PORT = int(os.getenv("PORT", "5001"))
OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + OFFSET


server = socket.socket()

server.bind(("0.0.0.0", PORT))
server.listen()

while True:

    conn, addr = server.accept()

    request = conn.recv(1024).decode()

    if request == "CLOCK_REQUEST":

        conn.send(str(get_time()).encode())

    elif request.startswith("CORRECTION"):

        correction = float(request.split(":")[1])

        print("Correction received:", correction)

        conn.close()
        break

    conn.close()
