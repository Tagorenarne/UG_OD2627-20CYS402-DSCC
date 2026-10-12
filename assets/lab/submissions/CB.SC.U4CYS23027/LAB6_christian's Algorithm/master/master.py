import os, socket, threading, time
from datetime import datetime

HOST = "0.0.0.0"
PORT = int(os.environ.get("MASTER_PORT", 5000))
MASTER_OFFSET = float(os.environ.get("MASTER_OFFSET", 0))          # seconds
ARTIFICIAL_DELAY_MS = float(os.environ.get("ARTIFICIAL_DELAY_MS", 0))  # ms

def master_time():
    return time.time() + MASTER_OFFSET

def fmt(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode().strip()
        if data != "TIME_REQUEST":
            return
        print(f"[MASTER] TIME_REQUEST from {addr}", flush=True)
        if ARTIFICIAL_DELAY_MS > 0:
            time.sleep(ARTIFICIAL_DELAY_MS / 1000.0)
        t = master_time()
        conn.sendall(f"MASTER_TIME={t}".encode())
        print(f"[MASTER] Replied {fmt(t)} to {addr} (delay={ARTIFICIAL_DELAY_MS}ms)", flush=True)
    finally:
        conn.close()

def main():
    print("===== Cristian's Algorithm - Time Server =====", flush=True)
    print(f"Listening on {HOST}:{PORT} | offset={MASTER_OFFSET}s | delay={ARTIFICIAL_DELAY_MS}ms\n", flush=True)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(16)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()