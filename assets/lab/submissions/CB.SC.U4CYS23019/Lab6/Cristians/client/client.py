import socket
import time
import os
from datetime import datetime

CLIENT_ID = os.getenv("CLIENT_ID")
CLOCK_OFFSET = int(os.getenv("CLOCK_OFFSET"))

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

local_time = time.time() + CLOCK_OFFSET

print("\n========== CRISTIAN'S ALGORITHM ==========")
print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Clock   : {format_time(local_time)}")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

T1 = time.time() + CLOCK_OFFSET

client.connect((MASTER_HOST, MASTER_PORT))
client.send("TIME_REQUEST".encode())

master_time = float(client.recv(1024).decode())

T2 = time.time() + CLOCK_OFFSET

client.close()

RTT = T2 - T1
estimated_delay = RTT / 2

corrected_clock = master_time + estimated_delay

final_error = abs(corrected_clock - master_time)

print(f"\nT1              : {format_time(T1)}")
print(f"Master Time     : {format_time(master_time)}")
print(f"T2              : {format_time(T2)}")

print(f"\nRTT             : {round(RTT*1000,2)} ms")
print(f"Estimated Delay : {round(estimated_delay*1000,2)} ms")

print(f"\nCorrected Clock : {format_time(corrected_clock)}")
print(f"Final Error     : {round(final_error*1000,2)} ms")

print("==========================================\n")
