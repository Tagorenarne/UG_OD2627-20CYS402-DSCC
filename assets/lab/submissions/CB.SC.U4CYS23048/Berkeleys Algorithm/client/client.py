import socket
import time
import os

name = os.environ.get("CLIENT_ID", "client")
offset = float(os.environ.get("CLOCK_OFFSET", "0"))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 5000))
sock.listen(5)

print(f"{name} started")
print(f"Clock offset = {offset} seconds")

while True:
    conn, addr = sock.accept()

    try:
        msg = conn.recv(1024).decode().strip()

        if msg == "TIME":
            adjusted_time = time.time() + offset
            conn.sendall(str(adjusted_time).encode())

            print(f"{name}: time sent")

        elif msg.startswith("CORRECTION:"):
            value = msg.replace("CORRECTION:", "", 1).strip()
            adjustment = float(value)

            offset += adjustment

            print(f"{name}: adjustment = {adjustment:.2f}s")
            print(f"{name}: current offset = {offset:.2f}s")

    finally:
        conn.close()
