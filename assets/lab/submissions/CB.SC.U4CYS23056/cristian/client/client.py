import os
import socket
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
MASTER_HOST = "clock-master"
MASTER_PORT = 5000


def get_logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp)) + f".{int((timestamp % 1) * 1000):03d}"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((MASTER_HOST, MASTER_PORT))

# Measure round-trip time with a monotonic clock, which is not affected by clock offsets.
t1 = time.monotonic()
client.sendall(f"TIME_REQUEST|{CLIENT_ID}".encode())
response = client.recv(1024).decode().strip()
t2 = time.monotonic()

parts = response.split("|")
if len(parts) != 3 or parts[0] != "TIME":
    client.close()
    raise RuntimeError(f"Unexpected response from time server: {response}")

server_time = float(parts[2])
rtt = t2 - t1
estimated_delay = rtt / 2.0
initial_clock = get_logical_time()
# Cristian's algorithm: estimate server time at reply receipt as server timestamp + RTT/2.
estimated_clock = server_time + estimated_delay
correction = estimated_clock - initial_clock
final_clock = initial_clock + correction

print("\n========================================")
print("       CRISTIAN CLOCK CLIENT")
print("========================================")
print(f"Client ID             : {CLIENT_ID}")
print(f"Configured clock offset: {CLOCK_OFFSET:+.3f} sec")
print("----------------------------------------")
print(f"Initial local clock   : {format_time(initial_clock)}")
print(f"Server timestamp      : {format_time(server_time)}")
print(f"Round-trip time (RTT) : {rtt * 1000:.2f} ms")
print(f"Estimated one-way delay: {estimated_delay * 1000:.2f} ms")
print(f"Estimated server time : {format_time(estimated_clock)}")
print(f"Clock correction      : {correction:+.3f} sec")
print(f"Final synchronized    : {format_time(final_clock)}")
print("========================================\n")

client.sendall(
    f"RESULT|{CLIENT_ID}|{initial_clock}|{estimated_clock}|{rtt}|{final_clock}".encode()
)
client.close()
