import socket
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print("======================================")
print("     CRISTIAN TIME SERVER")
print("======================================")
print(f"Server listening on port {PORT}")

while True:
    conn, addr = server_socket.accept()

    print(f"\nClient connected: {addr}")

    request = conn.recv(1024)

    if request:
        # Actual server system time
        server_time = time.time()

        print("Server system time:",
              datetime.fromtimestamp(server_time))

        # Send server time to client
        conn.send(str(server_time).encode())

    conn.close()
