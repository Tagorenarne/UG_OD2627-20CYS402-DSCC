import socket
import datetime
import os
import time

SERVER_HOST = os.getenv("SERVER_HOST", "clock-master")
SERVER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client1")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

print("")
print("========================================")
print("       CRISTIAN'S ALGORITHM")
print("========================================")

print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Offset  : {CLOCK_OFFSET:+.1f} seconds")


def logical_time():
    return datetime.datetime.now() + datetime.timedelta(
        seconds=CLOCK_OFFSET
    )


initial_time = logical_time()

print(f"Initial Clock   : {initial_time}")
print("")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# T1
t1 = time.perf_counter()
t1_clock = logical_time()

# Connect to master
s.connect((SERVER_HOST, SERVER_PORT))

# Send request
s.sendall(b"TIME_REQUEST")

# Receive master time
data = s.recv(1024)

# T2
t2 = time.perf_counter()
t2_clock = logical_time()

master_time = datetime.datetime.fromisoformat(
    data.decode()
)

s.close()

# RTT
rtt = t2 - t1

# Estimated one-way delay
estimated_delay = rtt / 2

# Cristian's corrected time
corrected_time = master_time + datetime.timedelta(
    seconds=estimated_delay
)

# Actual logical client time
actual_client_time = t2_clock

# Synchronization error
# Compare corrected time with the master's returned time
error = abs(
    (corrected_time - master_time).total_seconds()
)

print(f"T1              : {t1_clock}")
print(f"Master Time     : {master_time}")
print(f"T2              : {t2_clock}")
print("")

print(f"RTT             : {rtt * 1000:.3f} ms")
print(f"Estimated Delay : {estimated_delay * 1000:.3f} ms")
print("")

print(f"Corrected Clock : {corrected_time}")
print(f"Final Error     : {error * 1000:.3f} ms")

print("")
print("========================================")