import socket
import time
import os
from datetime import datetime

server_host = "0.0.0.0"
server_port = 5000

clock_offset = float(os.getenv("CLOCK_OFFSET", "0"))
response_delay = float(os.getenv("RESPONSE_DELAY", "0"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((server_host, server_port))
server_socket.listen(5)

print("MASTER TIME SERVER")
print("=" * 35)
print(f"Clock Offset   : {clock_offset:+.2f} seconds")
print(f"Response Delay : {response_delay * 1000:.0f} ms")
print(f"Listening On   : {server_host}:{server_port}")
print()

while True:

    client_connection, client_address = server_socket.accept()

    print(f"Request received from {client_address}")

    if response_delay > 0:
        time.sleep(response_delay)

    server_time = time.time() + clock_offset

    server_time_display = datetime.fromtimestamp(
        server_time
    ).strftime("%Y-%m-%d %H:%M:%S.%f")

    print(f"Master Time: {server_time_display}")

    client_connection.sendall(str(server_time).encode())

    client_connection.close()
