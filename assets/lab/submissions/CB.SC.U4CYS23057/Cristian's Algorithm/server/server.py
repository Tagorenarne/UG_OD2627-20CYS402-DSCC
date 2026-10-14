import socket
import time

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 8888))
server.listen()
print("Time server running on port 8888")

while True:
    conn, addr = server.accept()
    conn.recv(1024)                  
    server_time = time.time()        
    conn.send(str(server_time).encode())
    print(f"Sent time {server_time:.6f} to {addr[0]}")
    conn.close()
