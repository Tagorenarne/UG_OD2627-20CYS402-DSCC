import socket
import time
import os

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

def logical_time():
    return time.time() + CLOCK_OFFSET


print("========================================")
print("       CRISTIAN'S CLOCK ALGORITHM")
print("========================================")

print(f"Client ID     : {CLIENT_ID}")
print(f"Clock Offset  : {CLOCK_OFFSET} seconds")

while True:

    try:
        # T1
        T1 = logical_time()

        # Connect to master
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((MASTER_HOST, MASTER_PORT))

        # Send request
        client.send(b"TIME_REQUEST")

        # Receive master time
        data = client.recv(1024)

        # T2
        T2 = logical_time()

        master_time = float(data.decode())

        # Cristian's Algorithm
        RTT = T2 - T1
        estimated_delay = RTT / 2

        corrected_time = master_time + estimated_delay

        current_time = logical_time()

        error_before = abs(current_time - master_time)
        error_after = abs(corrected_time - master_time)

        print()
        print("----------------------------------------")
        print(f"Client ID       : {CLIENT_ID}")
        print(f"Initial Clock   : {current_time:.6f}")
        print(f"T1              : {T1:.6f}")
        print(f"Master Time     : {master_time:.6f}")
        print(f"T2              : {T2:.6f}")
        print(f"RTT             : {RTT * 1000:.2f} ms")
        print(f"Estimated Delay : {estimated_delay * 1000:.2f} ms")
        print(f"Corrected Clock : {corrected_time:.6f}")
        print(f"Error Before    : {error_before:.6f} sec")
        print(f"Error After     : {error_after:.6f} sec")
        print("----------------------------------------")

        client.close()

        time.sleep(5)

    except Exception as e:
        print("Waiting for master...")
        time.sleep(2)