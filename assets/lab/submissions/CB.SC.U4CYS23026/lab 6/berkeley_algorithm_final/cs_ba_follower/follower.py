import os, socket, time, threading

PORT = 5000
CLIENT_ID = os.getenv("CLIENT_ID", "client")
OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

def logical_clock():
    return time.time() + OFFSET

def handle(conn):
    global OFFSET
    try:
        request = conn.recv(1024).decode().strip()
        if request == "CLOCK_REQUEST":
            conn.sendall(str(logical_clock()).encode())
        elif request.startswith("CORRECTION"):
            correction = float(request.split()[1])
            # Keep the requested logical correction for this process.
            # Store it in OFFSET so the displayed clock reflects synchronization.
            OFFSET += correction
            conn.sendall(b"OK")
    finally:
        conn.close()

print(f"[{CLIENT_ID}] Starting with offset {OFFSET:+.1f} sec")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", PORT))
server.listen(10)

while True:
    conn, _ = server.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
