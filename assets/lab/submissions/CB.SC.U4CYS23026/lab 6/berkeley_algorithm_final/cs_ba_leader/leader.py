import os, socket, time
from datetime import datetime

PORT = 5000
CLIENTS = ["cs_ba_follower1", "cs_ba_follower2", "cs_ba_follower3", "cs_ba_follower4"]
RETRIES = 30
RETRY_DELAY = 0.5

def fmt(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

def request_clock(name):
    last = None
    for _ in range(RETRIES):
        try:
            with socket.create_connection((name, PORT), timeout=2) as s:
                s.sendall(b"CLOCK_REQUEST")
                data = s.recv(1024).decode().strip()
                return float(data)
        except Exception as e:
            last = e
            time.sleep(RETRY_DELAY)
    raise RuntimeError(f"Could not contact {name}: {last}")

print("========== BERKELEY ALGORITHM ==========")

master_offset = float(os.getenv("CLOCK_OFFSET", "0"))
master_clock = time.time() + master_offset

clocks = {"Master": master_clock}
offsets = {"Master": master_offset}

for i, name in enumerate(CLIENTS, 1):
    clocks[f"Client {i}"] = request_clock(name)

print("\nInitial Clocks")
print(f"Master       : {fmt(clocks['Master'])}")
for i in range(1, 5):
    print(f"Client {i}     : {fmt(clocks[f'Client {i}'])}")

print("\n------------------------------------------")
print("Clock Offsets")

# Use the master as the reference at the polling instant.
for i in range(1, 5):
    offsets[f"Client {i}"] = clocks[f"Client {i}"] - clocks["Master"]

print(f"Master       : {offsets['Master']:+.1f} sec")
for i in range(1, 5):
    print(f"Client {i}     : {offsets[f'Client {i}']:+.1f} sec")

average = sum(offsets.values()) / len(offsets)
print(f"\nAverage Offset: {average:+.1f} sec")

print("\n------------------------------------------")
print("Corrections")

corrections = {}
corrections["Master"] = average - offsets["Master"]
print(f"Master       : {corrections['Master']:+.1f} sec")

for i, name in enumerate(CLIENTS, 1):
    key = f"Client {i}"
    corrections[key] = average - offsets[key]
    try:
        with socket.create_connection((name, PORT), timeout=2) as s:
            s.sendall(f"CORRECTION {corrections[key]}".encode())
            s.recv(1024)
    except Exception as e:
        print(f"Warning: correction failed for {key}: {e}")
    print(f"Client {i}     : {corrections[key]:+.1f} sec")

master_final = clocks["Master"] + corrections["Master"]
print("\n------------------------------------------")
print("Final Clocks")
print(f"Master       : {fmt(master_final)}")

for i in range(1, 5):
    final = clocks[f"Client {i}"] + corrections[f"Client {i}"]
    print(f"Client {i}     : {fmt(final)}")

print("\nSynchronization complete.")
