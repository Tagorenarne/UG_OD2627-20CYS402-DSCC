import socket
import os
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

PORT = 5000
MASTER_HOST = "clock-master"

start_time = time.time()


def get_clock():
    elapsed = time.time() - start_time
    return elapsed + CLOCK_OFFSET


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", PORT))
server.listen(5)

print(f"[{CLIENT_ID}] Started")
print(f"[{CLIENT_ID}] Clock offset = {CLOCK_OFFSET:+.1f} seconds")

while True:
    connection, address = server.accept()

    request = connection.recv(1024).decode()

    if request == "CLOCK_REQUEST":
        current_clock = get_clock()

        response = f"{current_clock}"

        connection.send(response.encode())

        print(
            f"[{CLIENT_ID}] Clock = {current_clock:+.2f} sec"
        )

    elif request.startswith("CORRECTION:"):
        correction = float(request.split(":")[1])

        before = get_clock()

        CLOCK_OFFSET += correction

        after = get_clock()

        print(
            f"[{CLIENT_ID}] Correction = {correction:+.2f} sec"
        )
        print(
            f"[{CLIENT_ID}] Before = {before:.2f}, "
            f"After = {after:.2f}"
        )

    connection.close()
