#!/usr/bin/env python3
import socket
import time
from datetime import datetime
import json

HOST = '0.0.0.0'
PORT = 8888

def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("==================================================")
    print(f"[*] Cristian's Algorithm - Time Server Started")
    print(f"[*] Listening on {HOST}:{PORT}")
    print(f"[*] Current Server Time: {format_time(time.time())}")
    print("==================================================")

    try:
        while True:
            conn, addr = server_socket.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                
                # Capture server timestamp immediately upon receiving request
                t_server = time.time()
                t_server_str = format_time(t_server)
                
                print(f"[+] Sync request from {addr[0]}:{addr[1]}")
                print(f"    Server timestamp generated: {t_server_str} ({t_server:.6f})")
                
                response_payload = {
                    "server_time": t_server,
                    "server_time_str": t_server_str
                }
                
                conn.sendall(json.dumps(response_payload).encode('utf-8'))
                print(f"    Timestamp sent to client.")
    except KeyboardInterrupt:
        print("\n[*] Server shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    run_server()
