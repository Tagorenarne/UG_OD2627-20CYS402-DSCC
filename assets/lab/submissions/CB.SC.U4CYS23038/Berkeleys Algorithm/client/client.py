import socket
import time
import os

server_host = os.getenv("SERVER_HOST", "server")
server_port = 5000

clock_offset = float(os.getenv("CLOCK_OFFSET", "0"))


def get_current_time():
    return time.time() + clock_offset


def main():
    global clock_offset

    client_time = get_current_time()
    print(f"[CLIENT] Current time: {client_time:.3f}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    client_socket.sendall(str(client_time).encode())
    print(f"[CLIENT] Sent time: {client_time:.3f}")

    received_data = client_socket.recv(1024).decode()
    time_correction = float(received_data)
    print(f"[CLIENT] Received correction: {time_correction:+.3f}")

    clock_offset += time_correction
    print(f"[CLIENT] New time: {get_current_time():.3f}")

    client_socket.close()

if __name__ == "__main__":
    main()
