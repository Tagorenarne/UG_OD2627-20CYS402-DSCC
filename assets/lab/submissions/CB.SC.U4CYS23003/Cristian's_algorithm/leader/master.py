import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

DELAY = float(os.getenv("MASTER_DELAY", "0"))

def get_master_time():
    return time.time()

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print("=" * 50)
print("MASTER TIME SERVER STARTED")
print(f"Port : {PORT}")
print(f"Artificial Delay : {DELAY} seconds")
print("=" * 50)

while True:
    client_socket, client_address = server_socket.accept()
    print(f"\nClient connected: {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            request = data.decode()

            if request == "TIME_REQUEST":
                print("TIME_REQUEST received")

                # simulate processing/network delay
                if DELAY > 0:
                    time.sleep(DELAY)
                master_time = get_master_time()
                response = str(master_time)

                client_socket.sendall(response.encode())
                print("Master Time Sent:",datetime.fromtimestamp(master_time))

    except Exception as e:
        print("Client error:",e)

    finally:
        client_socket.close()
        print("Client disconnected")