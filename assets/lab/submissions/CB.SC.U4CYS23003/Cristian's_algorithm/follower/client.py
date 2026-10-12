import socket
import time
import os
from datetime import datetime

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

SYNC_INTERVAL = 5

def logical_time():
    return time.time() + CLOCK_OFFSET

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

print("=" * 55)
print("CRISTIAN'S CLOCK SYNCHRONIZATION")
print("=" * 55)

print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Offset  : {CLOCK_OFFSET:+.2f} seconds")
print(f"Master          : {SERVER_HOST}:{SERVER_PORT}")

print()
print("Connecting to master...")

client_socket.connect((SERVER_HOST, SERVER_PORT))

print("Connected to master.")

try:

    while True:
        # T1: client logical time before request
        T1 = logical_time()

        # Send request
        client_socket.sendall(b"TIME_REQUEST")

        # Receive master timestamp
        data = client_socket.recv(1024)

        # T2: client logical time after response
        T2 = logical_time()

        if not data:
            print("Master disconnected.")
            break

        master_time = float(data.decode())
        # Cristian's Algorithm
        RTT = T2 - T1
        estimated_delay = RTT / 2
        corrected_clock = (master_time + estimated_delay)
        # Compare corrected clock with master time
        final_error = (corrected_clock - master_time)

        print()
        print("=" * 55)
        print("CRISTIAN'S ALGORITHM")
        print("=" * 55)
        print(f"Client ID       : {CLIENT_ID}")
        print(f"Initial Offset  : "f"{CLOCK_OFFSET:+.3f} s")
        print()
        print(f"T1              : "f"{datetime.fromtimestamp(T1)}")
        print(f"Master Time     : "f"{datetime.fromtimestamp(master_time)}")
        print(f"T2              : "f"{datetime.fromtimestamp(T2)}")
        print()
        print(f"RTT             : "f"{RTT * 1000:.3f} ms")
        print(f"Estimated Delay : "f"{estimated_delay * 1000:.3f} ms")
        print()
        print(f"Client Clock    : "f"{datetime.fromtimestamp(T2)}")
        print(f"Corrected Clock : "f"{datetime.fromtimestamp(corrected_clock)}")
        print()
        print(f"Final Error     : "f"{final_error * 1000:.3f} ms")
        print("=" * 55)
        time.sleep(SYNC_INTERVAL)

except KeyboardInterrupt:
    print("\nClient stopped.")

except Exception as e:
    print("Client error:",e)

finally:
    client_socket.close()