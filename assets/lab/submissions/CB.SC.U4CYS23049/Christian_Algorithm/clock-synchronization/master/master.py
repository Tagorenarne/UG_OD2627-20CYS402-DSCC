import socket
import datetime
import os
import time

HOST = "0.0.0.0"
PORT = 5000

NETWORK_DELAY = float(os.getenv("NETWORK_DELAY", "0"))

print("========================================")
print("       CRISTIAN CLOCK MASTER")
print("========================================")
print(f"Port           : {PORT}")
print(f"Network Delay  : {NETWORK_DELAY} seconds")
print("")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(10)

print("Master server started...")
print("Waiting for clients...")

while True:

    connection, address = server.accept()

    print(f"Request received from {address}")

    # Artificial delay for experiments
    if NETWORK_DELAY > 0:
        time.sleep(NETWORK_DELAY)

    # Master logical time
    master_time = datetime.datetime.now()

    message = master_time.isoformat()

    connection.sendall(message.encode())

    print(f"Master Time : {master_time}")
    print("Response sent")
    print("----------------------------------------")

    connection.close()