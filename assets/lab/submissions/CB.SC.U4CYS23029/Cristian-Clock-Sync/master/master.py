import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
DELAY_MS = float(os.getenv("DELAY_MS", "0"))


def get_logical_time():
    return time.time() + CLOCK_OFFSET


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("====================================")
print("      CRISTIAN'S TIME SERVER")
print("====================================")
print(f"Clock Offset : {CLOCK_OFFSET} seconds")
print(f"Artificial Delay : {DELAY_MS} ms")
print(f"Listening on : {HOST}:{PORT}")
print()

while True:
    conn, addr = server.accept()

    request = conn.recv(1024).decode()

    if request == "TIME_REQUEST":

        # Artificial network/processing delay
        time.sleep(DELAY_MS / 1000)

        current_time = get_logical_time()

        print(f"Request received from {addr}")
        print(f"Master Time: {current_time:.6f}")

        response = str(current_time)
        conn.sendall(response.encode())

    conn.close()