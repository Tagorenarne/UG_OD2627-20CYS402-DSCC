import socket
import time
import os

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5001"))

# Artificial initial clock difference
INITIAL_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

clock_offset = INITIAL_OFFSET


def get_time():
    return time.time() + clock_offset


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print(f"Follower started on port {PORT}")
print(f"Initial clock offset: {clock_offset:+.3f}s")


while True:

    conn, addr = server.accept()

    message = conn.recv(1024).decode()

    if message == "GET_TIME":

        current_time = get_time()

        conn.sendall(
            str(current_time).encode()
        )

        print(
            f"Sent clock: {current_time:.3f}"
        )

    elif message.startswith("ADJUST"):

        adjustment = float(
            message.split()[1]
        )

        clock_offset += adjustment

        print(
            f"Clock adjusted by "
            f"{adjustment:+.3f}s"
        )

        print(
            f"New clock offset: "
            f"{clock_offset:+.3f}s"
        )

        conn.sendall(b"OK")

    conn.close()