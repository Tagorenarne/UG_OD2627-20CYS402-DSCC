import os
import socket
import time
from datetime import datetime

CLIENT_ID = os.getenv("CLIENT_ID", "client")
OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
MASTER = os.getenv("MASTER_HOST", "clock-master")
PORT = 5000


def clock():
    return time.time() + OFFSET


def fmt(t):
    return datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def connect():
    # wait until the master is ready
    while True:
        try:
            return socket.create_connection((MASTER, PORT))
        except OSError:
            time.sleep(1)


initial_clock = clock()
sock = connect()

T1 = clock()                                   # Step 1: time before request
sock.send(f"TIME_REQUEST ({CLIENT_ID})".encode())   # Step 2: send request
master_time = float(sock.recv(1024).decode())  # Step 3: receive master time
T2 = clock()                                   # Step 4: time after response
reference = time.time()                        # real time (master offset is 0)
sock.close()

rtt = T2 - T1                                  # Step 5
delay = rtt / 2                                # Step 6
corrected = master_time + delay                # Step 7
error = corrected - reference

print(f"""
========== CRISTIAN'S ALGORITHM ==========

Client ID       : {CLIENT_ID}
Initial Clock   : {fmt(initial_clock)}

T1              : {fmt(T1)}
Master Time     : {fmt(master_time)}
T2              : {fmt(T2)}

RTT             : {rtt * 1000:.0f} ms
Estimated Delay : {delay * 1000:.0f} ms

Corrected Clock : {fmt(corrected)}
Final Error     : {error * 1000:.0f} ms
""")
