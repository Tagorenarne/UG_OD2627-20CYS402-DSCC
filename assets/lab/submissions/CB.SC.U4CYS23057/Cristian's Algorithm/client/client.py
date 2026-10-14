import socket
import time
import os

HOST = os.environ.get("SERVER_HOST", "time-server")
PORT = 8888
drift = 12.345678

def client_clock():
    return time.time() + drift

time.sleep(2)  

for i in range(1, 4):
    s = socket.socket()
    s.connect((HOST, PORT))

    t0 = client_clock()                          
    s.send(b"TIME")
    server_time = float(s.recv(1024).decode())   
    t1 = client_clock()                          
    s.close()

    rtt = t1-t0
    new_time = server_time+rtt/2
    offset = new_time-t1
    drift+=offset                             

    print(f"Round {i} ")
    print(f"T0: {t0:.6f}")
    print(f"Server time : {server_time:.6f}")
    print(f"T1: {t1:.6f}")
    print(f"RTT: {rtt * 1000:.3f} ms")
    print(f"Offset: {offset:+.6f} s")
    print(f"Synced time: {new_time:.6f}\n")

    time.sleep(2)
