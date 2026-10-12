import socket
import time
import os

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp)) + \
           f".{int((timestamp % 1) * 1000):03d}"


print("==========================================")
print("       CRISTIAN'S CLOCK SYNCHRONIZATION")
print("==========================================")
print(f"Client ID       : {CLIENT_ID}")
print(f"Clock Offset    : {CLOCK_OFFSET:+.1f} seconds")
print(f"Initial Clock   : {format_time(logical_time())}")
print()

time.sleep(2)

try:
    # T1 - time immediately before sending request
    T1 = logical_time()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((MASTER_HOST, MASTER_PORT))
    client_socket.sendall(b"TIME_REQUEST")

    # Receive master's time
    data = client_socket.recv(1024)

    # T2 - time immediately after receiving response
    T2 = logical_time()

    client_socket.close()

    master_time = float(data.decode())

    # Cristian's algorithm
    RTT = T2 - T1
    estimated_delay = RTT / 2

    corrected_clock = master_time + estimated_delay

    # Error between corrected clock and master time
    final_error = abs(corrected_clock - master_time)

    print("T1              :", format_time(T1))
    print("Master Time     :", format_time(master_time))
    print("T2              :", format_time(T2))
    print()

    print(f"RTT             : {RTT * 1000:.2f} ms")
    print(f"Estimated Delay : {estimated_delay * 1000:.2f} ms")
    print()

    print("Corrected Clock :", format_time(corrected_clock))
    print(f"Final Error     : {final_error * 1000:.2f} ms")
    print()

    print("Synchronization completed successfully.")

except Exception as e:
    print("ERROR:", e)