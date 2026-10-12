import socket
import time
import json

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(5)
    print("[Server] Time Server started on port 8080...", flush=True)

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[Server] Connection accepted from {addr}", flush=True)
        
        # Get current system time
        current_time = time.time()
        
        # Send timestamp as JSON
        response = json.dumps({"server_time": current_time})
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    run_server()