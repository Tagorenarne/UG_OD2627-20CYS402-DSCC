import socket
import time
import os
from datetime import datetime, timezone, timedelta


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MASTER_HOST = os.getenv(
    "MASTER_HOST",
    "clock-master"
)

MASTER_PORT = int(
    os.getenv("MASTER_PORT", "5000")
)

CLIENT_ID = os.getenv(
    "CLIENT_ID",
    "client"
)

CLOCK_OFFSET = float(
    os.getenv("CLOCK_OFFSET", "0")
)

# Indian Standard Time (UTC +5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Synchronization correction
clock_correction = 0.0


# --------------------------------------------------
# Logical Clock
# --------------------------------------------------

def logical_clock():
    """
    Client logical clock.

    Before synchronization:

        System Time + CLOCK_OFFSET

    After synchronization:

        System Time
        + CLOCK_OFFSET
        + synchronization correction

    The actual operating-system clock is NOT changed.
    """

    return (
        time.time()
        + CLOCK_OFFSET
        + clock_correction
    )


# --------------------------------------------------
# Format timestamp in IST
# --------------------------------------------------

def format_time(timestamp):
    """
    Convert Unix timestamp to IST
    and display milliseconds.
    """

    return datetime.fromtimestamp(
        timestamp,
        IST
    ).strftime("%H:%M:%S.%f")[:-3]


# --------------------------------------------------
# Cristian's Algorithm
# --------------------------------------------------

def synchronize():

    global clock_correction

    print()
    print("=" * 55)
    print("           CRISTIAN'S ALGORITHM")
    print("=" * 55)

    # --------------------------------------------------
    # Initial client clock
    # --------------------------------------------------

    initial_clock = logical_clock()

    print(f"Client ID       : {CLIENT_ID}")

    print(
        f"Clock Offset    : "
        f"{CLOCK_OFFSET:+.3f} seconds"
    )

    print(
        f"Initial Clock   : "
        f"{format_time(initial_clock)} IST"
    )

    print()

    # --------------------------------------------------
    # T1
    # Client time immediately before request
    # --------------------------------------------------

    t1 = logical_clock()

    # --------------------------------------------------
    # Create socket
    # --------------------------------------------------

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        # --------------------------------------------------
        # Connect to master
        # --------------------------------------------------

        sock.connect(
            (
                MASTER_HOST,
                MASTER_PORT
            )
        )

        # --------------------------------------------------
        # Send TIME_REQUEST
        # --------------------------------------------------

        sock.sendall(
            b"TIME_REQUEST"
        )

        # --------------------------------------------------
        # Receive master's timestamp
        # --------------------------------------------------

        data = sock.recv(1024)

        # --------------------------------------------------
        # T2
        # Client time immediately after response
        # --------------------------------------------------

        t2 = logical_clock()

        # Convert master's timestamp
        master_time = float(
            data.decode()
        )

        # --------------------------------------------------
        # Cristian's Algorithm
        # --------------------------------------------------

        # Round-trip time
        rtt = t2 - t1

        # Estimated one-way network delay
        estimated_delay = rtt / 2

        # Estimated synchronized time
        corrected_clock = (
            master_time
            + estimated_delay
        )

        # --------------------------------------------------
        # Apply clock correction
        # --------------------------------------------------

        current_system_time = time.time()

        clock_correction = (
            corrected_clock
            - current_system_time
            - CLOCK_OFFSET
        )

        # --------------------------------------------------
        # Read corrected logical clock
        # --------------------------------------------------

        synchronized_client_clock = logical_clock()

        # --------------------------------------------------
        # Calculate final synchronization error
        # --------------------------------------------------

        final_error = abs(
            synchronized_client_clock
            - master_time
        )

        # --------------------------------------------------
        # Display results
        # --------------------------------------------------

        print(
            f"T1              : "
            f"{format_time(t1)} IST"
        )

        print(
            f"Master Time     : "
            f"{format_time(master_time)} IST"
        )

        print(
            f"T2              : "
            f"{format_time(t2)} IST"
        )

        print()

        print(
            f"RTT             : "
            f"{rtt * 1000:.2f} ms"
        )

        print(
            f"Estimated Delay : "
            f"{estimated_delay * 1000:.2f} ms"
        )

        print()

        print(
            f"Corrected Clock : "
            f"{format_time(synchronized_client_clock)} IST"
        )

        print(
            f"Final Error     : "
            f"{final_error * 1000:.2f} ms"
        )

        print()

        print("=" * 55)

    except Exception as e:

        print(
            f"[ERROR] Could not synchronize: {e}"
        )

    finally:

        sock.close()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    # Give the master time to start
    time.sleep(3)

    # Run Cristian's algorithm
    synchronize()