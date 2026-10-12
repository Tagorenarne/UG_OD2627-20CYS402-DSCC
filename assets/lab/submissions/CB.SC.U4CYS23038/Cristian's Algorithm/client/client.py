import socket
import time
import os
from datetime import datetime

server_host = "clock-master"
server_port = 5000

client_id = os.getenv("CLIENT_ID", "Client")
clock_offset = float(os.getenv("CLOCK_OFFSET", "0"))

def get_current_time():
    return time.time() + clock_offset

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

initial_time = get_current_time()

request_sent_time = get_current_time()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))

received_data = client_socket.recv(1024)

response_received_time = get_current_time()

client_socket.close()

server_time = float(received_data.decode())

round_trip_time = response_received_time - request_sent_time

estimated_delay = round_trip_time / 2

corrected_time = server_time + estimated_delay

initial_time_display = format_time(initial_time)
request_time_display = format_time(request_sent_time)
server_time_display = format_time(server_time)
response_time_display = format_time(response_received_time)
corrected_time_display = format_time(corrected_time)

actual_system_time = time.time()
final_error = abs(corrected_time - actual_system_time)

print()
print("CHRISTIAN'S CLOCK SYNCHRONIZATION")
print("=" * 40)

print(f"Client ID          : {client_id}")
print(f"Clock Offset       : {clock_offset:+.2f} seconds")
print()

print(f"Initial Clock      : {initial_time_display}")
print()

print(f"T1 - Request Sent  : {request_time_display}")
print(f"Server Time        : {server_time_display}")
print(f"T2 - Response Recv : {response_time_display}")
print()

print(f"Round-Trip Time    : {round_trip_time * 1000:.3f} ms")
print(f"Estimated Delay    : {estimated_delay * 1000:.3f} ms")
print()

print(f"Corrected Clock    : {corrected_time_display}")
print(f"Final Error        : {final_error * 1000:.3f} ms")
print()
