import socket
import time
import os

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

def get_logical_time():
    return time.time() + CLOCK_OFFSET

print("====================================")
print("      CRISTIAN'S CLOCK SYNC")
print("====================================")
print(f"Client ID     : {CLIENT_ID}")
print(f"Clock Offset  : {CLOCK_OFFSET} seconds")
print()

# Small delay so the master has time to start
time.sleep(2)

try:
    # T1 - time immediately before request
    t1 = get_logical_time()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((MASTER_HOST, MASTER_PORT))

    client.sendall(b"TIME_REQUEST")

    # Receive master's time
    data = client.recv(1024)

    # T2 - time immediately after response
    t2 = get_logical_time()

    client.close()

    master_time = float(data.decode())

    # Cristian's Algorithm
    rtt = t2 - t1
    estimated_delay = rtt / 2
    corrected_time = master_time + estimated_delay

    initial_clock = t1
    final_error = abs(corrected_time - master_time)

    print(f"T1              : {t1:.6f}")
    print(f"Master Time     : {master_time:.6f}")
    print(f"T2              : {t2:.6f}")
    print()
    print(f"RTT             : {rtt * 1000:.2f} ms")
    print(f"Estimated Delay : {estimated_delay * 1000:.2f} ms")
    print()
    print(f"Initial Clock   : {initial_clock:.6f}")
    print(f"Corrected Clock : {corrected_time:.6f}")
    print(f"Final Error     : {final_error * 1000:.2f} ms")

except Exception as e:
    print(f"Error: {e}")