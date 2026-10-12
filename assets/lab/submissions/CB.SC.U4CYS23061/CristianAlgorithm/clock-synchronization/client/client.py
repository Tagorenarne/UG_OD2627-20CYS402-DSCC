import socket
import datetime
import time
import os


# ============================================================
# CLIENT CONFIGURATION
# ============================================================

CLIENT_ID = os.getenv(
    "CLIENT_ID",
    "client"
)

INITIAL_CLOCK_OFFSET = float(
    os.getenv("CLOCK_OFFSET", "0")
)

CLOCK_OFFSET = INITIAL_CLOCK_OFFSET

MASTER_HOST = os.getenv(
    "MASTER_HOST",
    "master"
)

MASTER_PORT = int(
    os.getenv("MASTER_PORT", "5000")
)


# ============================================================
# LOGICAL CLOCK
# ============================================================

def logical_time():
    """
    Client logical clock.

    Logical Clock =
        System Clock + Current Logical Offset

    The operating system clock is NOT modified.
    """

    return (
        datetime.datetime.now()
        + datetime.timedelta(
            seconds=CLOCK_OFFSET
        )
    )


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(value):

    return value.strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )


# ============================================================
# REQUEST MASTER TIME
# ============================================================

def request_master_time():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(10)

    try:

        sock.connect(
            (
                MASTER_HOST,
                MASTER_PORT
            )
        )

        sock.sendall(
            b"TIME_REQUEST"
        )

        data = sock.recv(1024)

        if not data:

            raise RuntimeError(
                "Master returned an empty response"
            )

        return datetime.datetime.fromisoformat(
            data.decode()
        )

    finally:

        sock.close()


# ============================================================
# PROGRAM START
# ============================================================

print()
print("=" * 60)
print("          CRISTIAN'S CLOCK SYNCHRONIZATION")
print("=" * 60)

print(
    f"Client ID       : {CLIENT_ID}"
)

print(
    f"Initial Offset  : {INITIAL_CLOCK_OFFSET:+.1f} seconds"
)

print(
    f"Master          : {MASTER_HOST}:{MASTER_PORT}"
)


# ============================================================
# INITIAL CLOCK
# ============================================================

initial_clock = logical_time()

print(
    "Initial Clock   :",
    format_time(initial_clock)
)

print()


# ============================================================
# FIRST SYNCHRONIZATION REQUEST
# ============================================================

# T1 = client time immediately before request

T1 = logical_time()


# Request master time

master_time = request_master_time()


# T2 = client time immediately after response

T2 = logical_time()


# ============================================================
# RTT
# ============================================================

RTT = (
    T2 - T1
).total_seconds()


# ============================================================
# ESTIMATED ONE-WAY DELAY
# ============================================================

estimated_delay = RTT / 2


# ============================================================
# CRISTIAN'S CORRECTED CLOCK
# ============================================================

corrected_clock = (
    master_time
    + datetime.timedelta(
        seconds=estimated_delay
    )
)


# ============================================================
# UPDATE LOGICAL CLOCK
# ============================================================

system_time_now = datetime.datetime.now()

CLOCK_OFFSET = (
    corrected_clock
    - system_time_now
).total_seconds()


# ============================================================
# UPDATED CLIENT CLOCK
# ============================================================

updated_clock = logical_time()


# ============================================================
# VERIFICATION REQUEST
# ============================================================

time.sleep(0.01)


# Time immediately before verification request
V1 = logical_time()


# Master timestamp
verification_master_time = request_master_time()


# Time immediately after verification response
V2 = logical_time()


# ============================================================
# VERIFICATION RTT
# ============================================================

verification_RTT = (
    V2 - V1
).total_seconds()


verification_delay = (
    verification_RTT / 2
)


# ============================================================
# EXPECTED MASTER TIME AT CLIENT RECEIPT
# ============================================================

expected_master_time = (
    verification_master_time
    + datetime.timedelta(
        seconds=verification_delay
    )
)


# ============================================================
# FINAL SYNCHRONIZATION ERROR
# ============================================================

final_error = abs(
    (
        V2
        - expected_master_time
    ).total_seconds()
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print(
    "T1              :",
    format_time(T1)
)

print(
    "Master Time     :",
    format_time(master_time)
)

print(
    "T2              :",
    format_time(T2)
)

print()

print(
    f"RTT             : {RTT * 1000:.3f} ms"
)

print(
    f"Estimated Delay : "
    f"{estimated_delay * 1000:.3f} ms"
)

print()

print(
    "Corrected Clock :",
    format_time(corrected_clock)
)

print(
    "Updated Clock   :",
    format_time(updated_clock)
)

print()

print(
    "Verification Master Time :",
    format_time(
        verification_master_time
    )
)

print(
    f"Verification RTT         : "
    f"{verification_RTT * 1000:.3f} ms"
)

print(
    f"Verification Delay       : "
    f"{verification_delay * 1000:.3f} ms"
)

print(
    "Expected Master Time     :",
    format_time(
        expected_master_time
    )
)

print(
    "Verification Client Time :",
    format_time(V2)
)

print()

print(
    f"Final Error              : "
    f"{final_error * 1000:.3f} ms"
)

print("=" * 60)
print()
