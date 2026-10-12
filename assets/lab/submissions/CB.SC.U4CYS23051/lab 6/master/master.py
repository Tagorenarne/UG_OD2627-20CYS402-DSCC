import socket
import json
import time

MASTER_HOST = "0.0.0.0"
MASTER_PORT = 5000

CLIENTS = [
    ("client1", "clock-client1"),
    ("client2", "clock-client2"),
    ("client3", "clock-client3"),
    ("client4", "clock-client4")
]

# Optional outlier-handling enhancement
OUTLIER_THRESHOLD = 30.0

master_start_time = time.time()
master_offset = 0.0


def get_master_clock():
    return (time.time() - master_start_time) + master_offset


def send_request(host, port, request):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))

        sock.sendall(json.dumps(request).encode())

        response = sock.recv(4096).decode()

        sock.close()

        return json.loads(response)

    except Exception as e:
        print(f"Connection error with {host}: {e}")
        return None


def format_clock(seconds):
    sign = "+" if seconds >= 0 else "-"
    return f"{sign}{abs(seconds):.2f} sec"


print("=" * 60)
print("        BERKELEY CLOCK SYNCHRONIZATION")
print("=" * 60)

time.sleep(5)

master_clock = get_master_clock()

print("\nInitial Clocks")
print("-" * 60)

print(f"Master       : {master_clock:.2f} sec")

clock_values = {
    "Master": master_clock
}

for client_id, hostname in CLIENTS:

    response = send_request(
        hostname,
        5001,
        {"command": "CLOCK_REQUEST"}
    )

    if response:
        clock = response["clock"]
        clock_values[client_id] = clock

        print(f"{client_id:<12} : {clock:.2f} sec")


print("\n" + "-" * 60)
print("Clock Offsets")
print("-" * 60)

offsets = {}

for node, clock in clock_values.items():

    offset = clock - master_clock
    offsets[node] = offset

    print(f"{node:<12} : {format_clock(offset)}")


# ---------------------------------------------------------
# OUTLIER DETECTION
# ---------------------------------------------------------

participating_nodes = {}

for node, offset in offsets.items():

    if node == "Master":
        participating_nodes[node] = offset

    elif abs(offset) <= OUTLIER_THRESHOLD:
        participating_nodes[node] = offset

    else:
        print(
            f"OUTLIER EXCLUDED: {node} "
            f"({format_clock(offset)})"
        )


average_offset = (
    sum(participating_nodes.values())
    / len(participating_nodes)
)

print("\n" + "-" * 60)
print(
    f"Average Offset (after outlier removal): "
    f"{format_clock(average_offset)}"
)
print("-" * 60)


print("\nCorrections")
print("-" * 60)

corrections = {}

for node, offset in offsets.items():

    if node in participating_nodes:

        correction = average_offset - offset
        corrections[node] = correction

        print(
            f"{node:<12} : "
            f"{format_clock(correction)}"
        )

    else:

        corrections[node] = 0.0

        print(
            f"{node:<12} : EXCLUDED"
        )


# Apply master correction
master_offset += corrections["Master"]


# Send corrections to participating clients
for client_id, hostname in CLIENTS:

    correction = corrections[client_id]

    if client_id in participating_nodes:

        send_request(
            hostname,
            5001,
            {
                "command": "CORRECTION",
                "correction": correction
            }
        )


print("\n" + "-" * 60)
print("Final Clocks")
print("-" * 60)

time.sleep(1)

final_master_clock = get_master_clock()

print(
    f"Master       : {final_master_clock:.2f} sec"
)

for client_id, hostname in CLIENTS:

    response = send_request(
        hostname,
        5001,
        {"command": "CLOCK_REQUEST"}
    )

    if response:

        print(
            f"{client_id:<12} : "
            f"{response['clock']:.2f} sec"
        )


print("\n" + "=" * 60)
print("Synchronization completed.")
print("=" * 60)

while True:
    time.sleep(60)