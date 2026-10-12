import socket
import time
import os

PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
DELAY = float(os.getenv("DELAY", "0.1"))

start_time = time.time()


def get_clock():
    elapsed = time.time() - start_time
    return elapsed + CLOCK_OFFSET


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", PORT))
server.listen(10)

print("==========================================")
print("       CRISTIAN TIME SERVER")
print("==========================================")
print(f"Clock Offset : {CLOCK_OFFSET:+.2f} sec")
print(f"Artificial Delay : {DELAY * 1000:.0f} ms")
print(f"Listening on port {PORT}")
print("==========================================")

while True:

    connection, address = server.accept()

    request = connection.recv(1024).decode()

    if request == "TIME_REQUEST":

        print(f"\nRequest received from {address}")

        # Optional artificial delay
        if DELAY > 0:
            time.sleep(DELAY)

        master_time = get_clock()

        print(f"Sending master time: {master_time:.3f}")

        connection.send(str(master_time).encode())

    connection.close()
