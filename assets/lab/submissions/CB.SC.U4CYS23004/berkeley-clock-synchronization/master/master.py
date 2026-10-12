import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

CLIENTS = [
    "clock-client1",
    "clock-client2",
    "clock-client3",
    "clock-client4"
]


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


def get_client_clock(client_host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((client_host, PORT))

        sock.sendall(b"CLOCK_REQUEST")

        data = sock.recv(1024).decode().strip()

        sock.close()

        return float(data)

    except Exception as e:
        print(f"[ERROR] Could not contact {client_host}: {e}")
        return None


print("=" * 60)
print("          BERKELEY CLOCK SYNCHRONIZATION")
print("=" * 60)

print(f"Master initial offset : {CLOCK_OFFSET:+.2f} seconds")
print(f"Master initial clock  : {format_time(logical_time())}")

print("\nWaiting for clients...")

time.sleep(3)

print("\n" + "=" * 60)
print("INITIAL CLOCKS")
print("=" * 60)

master_clock = logical_time()

print(f"Master       : {format_time(master_clock)}")

client_clocks = {}

for client in CLIENTS:
    clock = get_client_clock(client)

    if clock is not None:
        client_clocks[client] = clock
        print(f"{client:<12}: {format_time(clock)}")
    else:
        print(f"{client:<12}: NO RESPONSE")


print("\n" + "=" * 60)
print("CLOCK OFFSETS")
print("=" * 60)

offsets = {}

offsets["Master"] = 0.0

print(f"Master       : {offsets['Master']:+.2f} sec")

for client, clock in client_clocks.items():

    offset = clock - master_clock

    offsets[client] = offset

    print(f"{client:<12}: {offset:+.2f} sec")


print("\n" + "=" * 60)
print("AVERAGE OFFSET")
print("=" * 60)

average_offset = sum(offsets.values()) / len(offsets)

print(f"Average Offset: {average_offset:+.2f} sec")


print("\n" + "=" * 60)
print("CORRECTIONS")
print("=" * 60)

corrections = {}

for node, offset in offsets.items():

    correction = average_offset - offset

    corrections[node] = correction

    print(f"{node:<12}: {correction:+.2f} sec")


print("\n" + "=" * 60)
print("APPLYING CORRECTIONS")
print("=" * 60)

# Apply correction to master
CLOCK_OFFSET += corrections["Master"]

print(
    f"Master correction: "
    f"{corrections['Master']:+.2f} sec"
)

# Send corrections to clients
for client in client_clocks:

    correction = corrections[client]

    try:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((client, PORT))

        message = f"CORRECTION:{correction}"

        sock.sendall(message.encode())

        response = sock.recv(1024).decode().strip()

        sock.close()

        print(
            f"{client:<12}: "
            f"sent {correction:+.2f} sec -> {response}"
        )

    except Exception as e:

        print(
            f"[ERROR] Could not send correction "
            f"to {client}: {e}"
        )


print("\n" + "=" * 60)
print("FINAL CLOCKS")
print("=" * 60)

print(
    f"Master       : "
    f"{format_time(logical_time())}"
)

for client in client_clocks:

    final_clock = get_client_clock(client)

    if final_clock is not None:

        print(
            f"{client:<12}: "
            f"{format_time(final_clock)}"
        )

print("\n" + "=" * 60)
print("BERKELEY SYNCHRONIZATION COMPLETE")
print("=" * 60)