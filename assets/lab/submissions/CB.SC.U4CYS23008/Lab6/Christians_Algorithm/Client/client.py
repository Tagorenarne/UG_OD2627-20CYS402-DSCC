import socket
import time
import os
from datetime import datetime


MASTER_HOST = os.getenv(
    "MASTER_HOST",
    "clock-master"
)

MASTER_PORT = 5000

CLIENT_ID = os.getenv(
    "CLIENT_ID",
    "Follower"
)

CLOCK_OFFSET = float(
    os.getenv("CLOCK_OFFSET", "0")
)


def logical_time():
    """
    Returns the simulated logical clock time.
    The actual system clock is not modified.
    """
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(
        timestamp
    ).strftime("%H:%M:%S.%f")[:-3]


print("=" * 65)
print("             CRISTIAN'S CLOCK SYNCHRONIZATION")
print("=" * 65)

print(f"Follower ID      : {CLIENT_ID}")
print(f"Initial Offset    : {CLOCK_OFFSET:+.2f} seconds")

initial_time = logical_time()

print(
    f"Initial Clock    : "
    f"{format_time(initial_time)}"
)

print()
print("Connecting to leader...")
print()


try:

    # ------------------------------------------------
    # STEP 1: Record T1
    # ------------------------------------------------

    T1 = logical_time()

    # Create socket
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Connect to leader
    client_socket.connect(
        (MASTER_HOST, MASTER_PORT)
    )

    # ------------------------------------------------
    # STEP 2: Send TIME_REQUEST
    # ------------------------------------------------

    client_socket.sendall(
        b"TIME_REQUEST"
    )

    # ------------------------------------------------
    # STEP 3: Receive leader time
    # ------------------------------------------------

    data = client_socket.recv(1024)

    # ------------------------------------------------
    # STEP 4: Record T2
    # ------------------------------------------------

    T2 = logical_time()

    client_socket.close()

    # Convert received leader time
    master_time = float(
        data.decode()
    )

    # ------------------------------------------------
    # STEP 5: Calculate RTT
    # ------------------------------------------------

    RTT = T2 - T1

    # ------------------------------------------------
    # STEP 6: Estimate one-way delay
    # ------------------------------------------------

    estimated_delay = RTT / 2

    # ------------------------------------------------
    # STEP 7: Calculate corrected time
    # ------------------------------------------------

    corrected_time = (
        master_time + estimated_delay
    )

    # ------------------------------------------------
    # Calculate synchronization error
    # ------------------------------------------------

    final_error = abs(
        corrected_time - master_time
    )

    # ------------------------------------------------
    # Display results
    # ------------------------------------------------

    print("=" * 65)

    print(
        f"Follower ID      : {CLIENT_ID}"
    )

    print(
        f"Initial Clock    : "
        f"{format_time(initial_time)}"
    )

    print(
        f"T1               : "
        f"{format_time(T1)}"
    )

    print(
        f"Leader Time      : "
        f"{format_time(master_time)}"
    )

    print(
        f"T2               : "
        f"{format_time(T2)}"
    )

    print()

    print(
        f"RTT              : "
        f"{RTT * 1000:.2f} ms"
    )

    print(
        f"Estimated Delay  : "
        f"{estimated_delay * 1000:.2f} ms"
    )

    print(
        f"Corrected Clock  : "
        f"{format_time(corrected_time)}"
    )

    print(
        f"Final Error      : "
        f"{final_error * 1000:.2f} ms"
    )

    print("=" * 65)


except Exception as e:

    print("=" * 65)
    print("Synchronization failed")
    print(f"Error: {e}")
    print("=" * 65)