import socket
import time

CLIENTS = {
    "client1": "clock-client1",
    "client2": "clock-client2",
    "client3": "clock-client3",
    "client4": "clock-client4"
}

PORT = 5000

master_offset = 0.0
start_time = time.time()


def get_master_clock():
    elapsed = time.time() - start_time
    return elapsed + master_offset


def get_client_clock(host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((host, PORT))

        sock.send(b"CLOCK_REQUEST")

        data = sock.recv(1024).decode()

        sock.close()

        return float(data)

    except Exception as e:
        print(f"Error contacting {host}: {e}")
        return None


def send_correction(host, correction):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((host, PORT))

        message = f"CORRECTION:{correction}"

        sock.send(message.encode())

        sock.close()

    except Exception as e:
        print(f"Error sending correction to {host}: {e}")


print("\n========== BERKELEY ALGORITHM ==========\n")

time.sleep(5)

# ------------------------------------------------
# Step 1: Get clocks
# ------------------------------------------------

master_clock = get_master_clock()

client_clocks = {}

for client_id, host in CLIENTS.items():
    clock = get_client_clock(host)

    if clock is not None:
        client_clocks[client_id] = clock

# ------------------------------------------------
# Step 2: Display initial clocks
# ------------------------------------------------

print("Initial Clocks\n")

print(f"Master       : {master_clock:.2f}")

for client_id, clock in client_clocks.items():
    print(f"{client_id:<12}: {clock:.2f}")

print("\n------------------------------------------")

# ------------------------------------------------
# Step 3: Calculate offsets
# ------------------------------------------------

offsets = {}

offsets["Master"] = 0.0

for client_id, clock in client_clocks.items():
    offsets[client_id] = clock - master_clock

print("\nClock Offsets\n")

for node, offset in offsets.items():
    print(f"{node:<12}: {offset:+.2f} sec")

# ------------------------------------------------
# Step 4: Average offset
# ------------------------------------------------

average_offset = sum(offsets.values()) / len(offsets)

print(f"\nAverage Offset: {average_offset:+.2f} sec")

print("\n------------------------------------------")

# ------------------------------------------------
# Step 5: Calculate corrections
# ------------------------------------------------

corrections = {}

for node, offset in offsets.items():
    corrections[node] = average_offset - offset

print("\nCorrections\n")

for node, correction in corrections.items():
    print(f"{node:<12}: {correction:+.2f} sec")

# ------------------------------------------------
# Step 6: Send corrections
# ------------------------------------------------

for client_id, host in CLIENTS.items():

    correction = corrections[client_id]

    send_correction(
        host,
        correction
    )

# ------------------------------------------------
# Step 7: Apply master correction
# ------------------------------------------------

master_offset += corrections["Master"]



# ------------------------------------------------
# Step 8: Final clocks
# ------------------------------------------------

print("\n------------------------------------------")

print("\nFinal Clocks\n")

final_master = get_master_clock()

print(f"Master       : {final_master:.2f}")

for client_id, host in CLIENTS.items():

    clock = get_client_clock(host)

    if clock is not None:
        print(f"{client_id:<12}: {clock:.2f}")

print("\n==========================================")
