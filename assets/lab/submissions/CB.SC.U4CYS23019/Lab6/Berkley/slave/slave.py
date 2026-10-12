import socket
import time
import os
import sys
from datetime import datetime

SLAVE_ID = os.getenv("SLAVE_ID", "Slave-1")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
PORT = int(os.getenv("PORT", "6000"))

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

current_offset = CLOCK_OFFSET

print(f"==================================================", flush=True)
print(f"       BERKELEY ALGORITHM - {SLAVE_ID} DAEMON      ", flush=True)
print(f"==================================================", flush=True)
print(f"Configured Clock Offset : {CLOCK_OFFSET:+.3f} s", flush=True)
print(f"Initial Logical Clock   : {format_time(time.time() + current_offset)}", flush=True)
print(f"Listening on port       : {PORT}", flush=True)
print(f"Status                  : Awaiting master requests...", flush=True)
print(f"==================================================\n", flush=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", PORT))
server.listen(5)

while True:
    try:
        conn, addr = server.accept()
        data = conn.recv(1024).decode().strip()
        
        if data == "GET_TIME" or data == "POLL":
            # Send current local logical clock timestamp
            local_time = time.time() + current_offset
            conn.sendall(f"{local_time}\n".encode())
            
            # Wait for master's calculated clock adjustment
            adj_data = conn.recv(1024).decode().strip()
            if adj_data.startswith("ADJUST:"):
                adjustment = float(adj_data.split(":")[1])
                before_adj_clock = time.time() + current_offset
                current_offset += adjustment
                after_adj_clock = time.time() + current_offset
                
                print(f"[{SLAVE_ID}] Received sync request from {addr[0]}", flush=True)
                print(f"[{SLAVE_ID}] Clock before adjustment : {format_time(before_adj_clock)}", flush=True)
                print(f"[{SLAVE_ID}] Adjustment received     : {adjustment:+.4f} s", flush=True)
                print(f"[{SLAVE_ID}] Synchronized Clock       : {format_time(after_adj_clock)}", flush=True)
                print(f"[{SLAVE_ID}] Updated Clock Offset     : {current_offset:+.4f} s", flush=True)
                print(f"[{SLAVE_ID}] Status: Synchronized successfully!\n", flush=True)
                
                conn.sendall("ACK\n".encode())
        conn.close()
    except Exception as e:
        print(f"[{SLAVE_ID}] Error handling connection: {e}", flush=True)
