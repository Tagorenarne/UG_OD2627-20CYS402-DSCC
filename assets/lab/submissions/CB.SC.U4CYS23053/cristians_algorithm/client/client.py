import socket
import time
import os

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET


print("==========================================")
print("       CRISTIAN'S CLOCK SYNCHRONIZATION")
print("==========================================")

print(f"Client ID     : {CLIENT_ID}")
print(f"Clock Offset  : {CLOCK_OFFSET} seconds")

initial_time = logical_time()

print(f"Initial Clock : {initial_time}")

print()
print("Synchronizing with master...")
print()

# T1
T1 = logical_time()

# Connect to master
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((MASTER_HOST, MASTER_PORT))

# Send request
client.sendall(b"TIME_REQUEST")

# Receive master time
data = client.recv(1024)

# T2
T2 = logical_time()

client.close()

# Convert master time
master_time = float(data.decode())

# Calculate RTT
RTT = T2 - T1

# Estimate one-way delay
estimated_delay = RTT / 2

# Cristian's algorithm
corrected_clock = master_time + estimated_delay

# Actual local clock after correction
actual_time = time.time()

# Synchronization error
final_error = abs(actual_time - corrected_clock)


print(f"T1            : {T1}")
print(f"Master Time   : {master_time}")
print(f"T2            : {T2}")
print()

print(f"RTT           : {RTT * 1000:.3f} ms")
print(f"Estimated Delay: {estimated_delay * 1000:.3f} ms")
print()

print(f"Corrected Clock: {corrected_clock}")
print(f"Final Error    : {final_error * 1000:.3f} ms")
print()

print("==========================================")