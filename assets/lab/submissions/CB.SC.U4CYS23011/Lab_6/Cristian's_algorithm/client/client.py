
import os
import time
import requests
from datetime import datetime

client_id = os.getenv("CLIENT_ID", "Client-1")
clock_offset = float(os.getenv("CLOCK_OFFSET", "0"))

# Logical clock
def logical_clock():
    return time.time() + clock_offset


# Convert timestamp to normal date and time
def format_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d-%m-%Y %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


print()
print("CRISTIAN ALGORITHM")
print()

# Initial logical clock
initial_time = logical_clock()

print(f"Client ID       : {client_id}")
print(f"Initial Clock   : {format_time(initial_time)}")
print()


# T1 - Client sends request
t1 = time.time()

try:
    response = requests.get(
        "http://clock-master:5000/time",
        timeout=5
    )

    # T2 - Client receives response
    t2 = time.time()

except requests.exceptions.RequestException as e:
    print("ERROR: Could not contact clock-master")
    print(e)
    exit(1)


# Get masters time
data = response.json()
master_time = data["server_time"]


# Calculate RTT
rtt = t2 - t1
rtt_ms = rtt * 1000

# Estimate one-way network delay
estimated_delay = rtt / 2
estimated_delay_ms = estimated_delay * 1000

corrected_clock = master_time + estimated_delay
# Calculate synchronization error
final_error = abs(corrected_clock - (master_time + estimated_delay))
final_error_ms = final_error * 1000

print(f"T1              : {format_time(t1)}")
print(f"Master Time     : {format_time(master_time)}")
print(f"T2              : {format_time(t2)}")
print()

print(f"RTT             : {rtt_ms:.0f} ms")
print(f"Estimated Delay : {estimated_delay_ms:.0f} ms")
print()

print(f"Corrected Clock : {format_time(corrected_clock)}")
print(f"Final Error     : {final_error_ms:.0f} ms")

print()
