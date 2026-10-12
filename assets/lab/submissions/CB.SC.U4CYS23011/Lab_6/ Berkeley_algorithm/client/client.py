import socket
import time
import os

SERVER_HOST = os.getenv("SERVER_HOST", "master")
SERVER_PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + CLOCK_OFFSET


def main():
    global CLOCK_OFFSET
    
    
    current_time = get_time()
    print(f"[CLIENT] Current time: {current_time:.3f}")

    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
  
    client.sendall(str(current_time).encode())
    print(f"[CLIENT] Sent time: {current_time:.3f}")
  
    data = client.recv(1024).decode()
    delay = float(data)
    print(f"[CLIENT] Received delay: {delay:+.3f}")

    CLOCK_OFFSET += delay
    print(f"[CLIENT] New time: {get_time():.3f}")

    client.close()


if __name__ == "__main__":
    main()
