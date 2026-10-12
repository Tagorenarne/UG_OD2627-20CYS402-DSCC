import socket
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo


# ==========================================
# Configuration
# ==========================================

HOST = "0.0.0.0"
PORT = int(os.getenv("MASTER_PORT", "5000"))

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

CLIENTS = [
    "client1",
    "client2",
    "client3",
    "client4"
]

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# Logical Clock
# ==========================================

def logical_clock():
    """
    Returns the current logical clock in Unix seconds.
    The configured CLOCK_OFFSET is applied to the
    current real time.
    """
    return time.time() + CLOCK_OFFSET


# ==========================================
# Format Clock as IST
# ==========================================

def format_clock(timestamp):
    """
    Convert timestamp to Indian Standard Time.
    """

    return datetime.fromtimestamp(
        timestamp,
        IST
    ).strftime("%H:%M:%S.%f")[:-3]


# ==========================================
# Start Server
# ==========================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen(10)

print("=" * 60)
print("BERKELEY CLOCK SYNCHRONIZATION")
print("=" * 60)

print(f"Master started on port {PORT}")
print("Time Zone: IST (Asia/Kolkata)")
print("Waiting for clients...")


# ==========================================
# Accept Clients
# ==========================================

connections = {}

while len(connections) < len(CLIENTS):

    conn, address = server.accept()

    print(f"Connection received from {address}")

    conn.sendall(b"CLOCK_REQUEST")

    data = conn.recv(1024).decode().strip()

    if data.startswith("CLOCK_RESPONSE"):

        parts = data.split("|")

        client_id = parts[1]
        clock_value = float(parts[2])

        connections[client_id] = {
            "socket": conn,
            "address": address,
            "clock": clock_value
        }

        print(f"Registered {client_id}")


print("\nAll clients connected.")
print("Starting Berkeley synchronization...\n")


# ==========================================
# Master Clock
# ==========================================

master_clock = logical_clock()


# ==========================================
# Initial Clocks
# ==========================================

print("=" * 60)
print("INITIAL CLOCKS")
print("=" * 60)

print(
    f"Master       : "
    f"{format_clock(master_clock)}"
)


# ==========================================
# Poll Clients
# ==========================================

for client_id, info in connections.items():

    info["socket"].sendall(
        b"CLOCK_REQUEST"
    )


# Receive responses

for client_id, info in connections.items():

    data = info["socket"].recv(1024).decode().strip()

    if data.startswith("CLOCK_RESPONSE"):

        parts = data.split("|")

        info["clock"] = float(parts[2])

        print(
            f"{client_id:<12}: "
            f"{format_clock(info['clock'])}"
        )


# ==========================================
# Calculate Offsets
# ==========================================

print("\n" + "-" * 60)
print("CLOCK OFFSETS")
print("-" * 60)

offsets = {}

offsets["Master"] = 0.0

for client_id, info in connections.items():

    client_offset = (
        info["clock"] - master_clock
    )

    offsets[client_id] = client_offset

    print(
        f"{client_id:<12}: "
        f"{client_offset:+.3f} sec"
    )

print(
    f"{'Master':<12}: "
    f"{offsets['Master']:+.3f} sec"
)


# ==========================================
# Calculate Average Offset
# ==========================================

total_offset = sum(offsets.values())

average_offset = (
    total_offset / len(offsets)
)

print("\n" + "-" * 60)

print(
    f"Average Offset: "
    f"{average_offset:+.3f} sec"
)


# ==========================================
# Calculate Corrections
# ==========================================

print("\n" + "-" * 60)
print("CORRECTIONS")
print("-" * 60)

corrections = {}

for node, offset in offsets.items():

    correction = (
        average_offset - offset
    )

    corrections[node] = correction

    print(
        f"{node:<12}: "
        f"{correction:+.3f} sec"
    )


# ==========================================
# Send Corrections
# ==========================================

for client_id, info in connections.items():

    correction = corrections[client_id]

    message = (
        f"CORRECTION|{correction}"
    )

    info["socket"].sendall(
        message.encode()
    )


# ==========================================
# Apply Master's Correction
# ==========================================

CLOCK_OFFSET += corrections["Master"]


# ==========================================
# Allow Clients to Apply Corrections
# ==========================================

time.sleep(1)


# ==========================================
# Final Clocks
# ==========================================

print("\n" + "=" * 60)
print("FINAL SYNCHRONIZED CLOCKS")
print("=" * 60)

final_master_clock = logical_clock()

print(
    f"Master       : "
    f"{format_clock(final_master_clock)}"
)

for client_id, info in connections.items():

    final_clock = (
        info["clock"]
        + corrections[client_id]
    )

    print(
        f"{client_id:<12}: "
        f"{format_clock(final_clock)}"
    )


print("\n" + "=" * 60)
print("BERKELEY SYNCHRONIZATION COMPLETE")
print("=" * 60)


# Keep master alive

while True:
    time.sleep(10)