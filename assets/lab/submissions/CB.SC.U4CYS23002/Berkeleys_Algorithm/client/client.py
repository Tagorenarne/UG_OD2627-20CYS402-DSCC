import socket
import time
import os

SERVER_HOST = os.getenv("SERVER_HOST", "server")
SERVER_PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + CLOCK_OFFSET


def main():
    global CLOCK_OFFSET
    
    # Get client's current time
    current_time = get_time()
    print(f"[CLIENT] Current time: {current_time:.3f}")

    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))

    # Send time to server
    client.sendall(str(current_time).encode())
    print(f"[CLIENT] Sent time: {current_time:.3f}")

    # Receive correction from server
    data = client.recv(1024).decode()
    delay = float(data)
    print(f"[CLIENT] Received delay: {delay:+.3f}")

    # Apply correction
    CLOCK_OFFSET += delay
    print(f"[CLIENT] New time: {get_time():.3f}")

    client.close()


if __name__ == "__main__":
    main()
