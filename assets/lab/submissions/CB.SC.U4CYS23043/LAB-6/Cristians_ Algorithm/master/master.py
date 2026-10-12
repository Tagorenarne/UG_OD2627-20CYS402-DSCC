import os, socket, threading, time
from datetime import datetime

SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("MASTER_PORT", 5000))
TIME_OFFSET = float(os.environ.get("MASTER_OFFSET", 0))          # seconds
NETWORK_DELAY_MS = float(os.environ.get("ARTIFICIAL_DELAY_MS", 0))  # ms

def get_master_time():
    return time.time() + TIME_OFFSET

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

def process_client(connection, address):
    try:
        request_data = connection.recv(1024).decode().strip()
        if request_data != "TIME_REQUEST":
            return
        print(f"[MASTER] TIME_REQUEST from {address}", flush=True)
        if NETWORK_DELAY_MS > 0:
            time.sleep(NETWORK_DELAY_MS / 1000.0)
        timestamp = get_master_time()
        connection.sendall(f"MASTER_TIME={timestamp}".encode())
        print(f"[MASTER] Replied {format_time(timestamp)} to {address} (delay={NETWORK_DELAY_MS}ms)", flush=True)
    finally:
        connection.close()

def main():
    print("===== Cristian's Algorithm - Time Server =====", flush=True)
    print(f"Listening on {SERVER_HOST}:{SERVER_PORT} | offset={TIME_OFFSET}s | delay={NETWORK_DELAY_MS}ms\n", flush=True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(16)
    while True:
        connection, address = server_socket.accept()
        threading.Thread(target=process_client, args=(connection, address), daemon=True).start()

if __name__ == "__main__":
    main()
