import socket
import time
from datetime import datetime

SERVER_HOST = "server"
SERVER_PORT = 5050

print("Connecting to Cristian Time Server...")

# Try connecting until the server is ready
while True:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Time when request is sent
        request_time = time.time()

        client_socket.connect((SERVER_HOST, SERVER_PORT))

        print("Connected to server!")
        break

    except ConnectionRefusedError:
        print("Server not ready. Retrying...")
        time.sleep(1)

# Send request
client_socket.send(b"TIME")

# Receive server time
data = client_socket.recv(1024)

# Time when response is received
receive_time = time.time()

server_time = float(data.decode())

client_socket.close()

# Calculate RTT
rtt = receive_time - request_time

# Cristian's Algorithm
estimated_server_time = server_time + (rtt / 2)

# Client's current time
client_time = receive_time

# Calculate clock skew
clock_skew = estimated_server_time - client_time

print("\n======================================")
print("       CRISTIAN'S ALGORITHM")
print("======================================")

print(f"Client request time    : {datetime.fromtimestamp(request_time)}")

print(f"Server time received   : {datetime.fromtimestamp(server_time)}")

print(f"Client receive time    : {datetime.fromtimestamp(receive_time)}")

print(f"Round Trip Time (RTT)  : {rtt:.6f} seconds")

print(f"Estimated server time  : {datetime.fromtimestamp(estimated_server_time)}")

print(f"Client current time    : {datetime.fromtimestamp(client_time)}")

print(f"Clock skew             : {clock_skew:.6f} seconds")

print(f"Time to set for client : {datetime.fromtimestamp(estimated_server_time)}")

print("======================================")
