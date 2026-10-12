import socket
import time
import os
from datetime import datetime

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    """
    Return the client's logical time.
    """
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    """
    Convert timestamp into HH:MM:SS.mmm format.
    """
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


print("=" * 50, flush=True)
print("       CRISTIAN'S CLOCK SYNCHRONIZATION", flush=True)
print("=" * 50, flush=True)

print(f"Client ID       : {CLIENT_ID}", flush=True)
print(f"Initial Offset  : {CLOCK_OFFSET} seconds", flush=True)

initial_time = logical_time()

print(
    f"Initial Clock   : {format_time(initial_time)}",
    flush=True
)

try:

    # --------------------------------------------------
    # Step 1: Record T1
    # --------------------------------------------------
    t1 = logical_time()

    # --------------------------------------------------
    # Step 2: Send TIME_REQUEST to master
    # --------------------------------------------------
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as client:

        client.connect((MASTER_HOST, MASTER_PORT))

        client.sendall(b"TIME_REQUEST")

        # --------------------------------------------------
        # Step 3: Receive master's logical time
        # --------------------------------------------------
        response = client.recv(1024).decode().strip()

    # --------------------------------------------------
    # Step 4: Record T2
    # --------------------------------------------------
    t2 = logical_time()

    master_time = float(response)

    # --------------------------------------------------
    # Step 5: Calculate RTT
    # --------------------------------------------------
    rtt = t2 - t1

    # --------------------------------------------------
    # Step 6: Estimate one-way delay
    # --------------------------------------------------
    estimated_delay = rtt / 2

    # --------------------------------------------------
    # Step 7: Calculate corrected/synchronized time
    # Cristian's Algorithm:
    #
    # Corrected Time = Master Time + RTT/2
    # --------------------------------------------------
    corrected_time = master_time + estimated_delay

    # Calculate how much the client clock needs to be adjusted.
    correction = corrected_time - t2

    # Update logical clock offset.
    CLOCK_OFFSET += correction

    # Read the corrected logical clock.
    final_time = logical_time()

    # Estimated synchronization error.
    final_error = final_time - corrected_time

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------
    print()
    print("=" * 50, flush=True)
    print("       SYNCHRONIZATION RESULT", flush=True)
    print("=" * 50, flush=True)

    print(
        f"T1              : {format_time(t1)}",
        flush=True
    )

    print(
        f"Master Time     : {format_time(master_time)}",
        flush=True
    )

    print(
        f"T2              : {format_time(t2)}",
        flush=True
    )

    print(
        f"RTT             : {rtt * 1000:.3f} ms",
        flush=True
    )

    print(
        f"Estimated Delay : {estimated_delay * 1000:.3f} ms",
        flush=True
    )

    print(
        f"Clock Correction: {correction * 1000:.3f} ms",
        flush=True
    )

    print(
        f"Corrected Clock : {format_time(final_time)}",
        flush=True
    )

    print(
        f"Final Error     : {final_error * 1000:.3f} ms",
        flush=True
    )

    print("=" * 50, flush=True)

except Exception as error:

    print(
        f"Synchronization failed: {error}",
        flush=True
    )