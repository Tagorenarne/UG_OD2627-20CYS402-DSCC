import os
import socket
import time
from datetime import datetime

offset = float(os.getenv("CLOCK_OFFSET", "0"))
CLIENTS = os.getenv("CLIENTS", "").split(",")
# Outlier handling (enhancement, NOT part of the basic Berkeley algorithm).
# Nodes with abs(offset) > THRESHOLD seconds are left out of the average. 0 = disabled.
THRESHOLD = float(os.getenv("OUTLIER_THRESHOLD", "0"))
PORT = 5000


def clock():
    return time.time() + offset


def fmt(t):
    return datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]


def send(host, message):
    # wait until the client is ready, then send one message and return the reply
    while True:
        try:
            sock = socket.create_connection((host, PORT))
            break
        except OSError:
            time.sleep(1)
    sock.send(message.encode())
    reply = sock.recv(1024).decode()
    sock.close()
    return reply


def poll_clocks():
    # returns {node: offset relative to master}
    offsets = {"Master": 0.0}
    for host in CLIENTS:
        client_time = float(send(host, "CLOCK_REQUEST"))
        offsets[host] = client_time - clock()
    return offsets


def show_clocks(offsets, with_error=False):
    # show every node's clock at the same instant (master clock + node offset)
    now = clock()
    for node, node_offset in offsets.items():
        line = f"{node:<14}: {fmt(now + node_offset)}"
        if with_error:
            line += f"   (error: {node_offset * 1000:+.0f} ms)"
        print(line)


print("========== BERKELEY ALGORITHM ==========\n")

# Step 1: master polls all nodes
offsets = poll_clocks()

print("Initial Clocks\n")
show_clocks(offsets)

# Step 2: offsets relative to the master
print("\n------------------------------------------\n")
print("Clock Offsets\n")
used = []
for node, node_offset in offsets.items():
    if THRESHOLD and abs(node_offset) > THRESHOLD:
        print(f"{node:<14}: {node_offset:+.3f} sec  (outlier - excluded from average)")
    else:
        print(f"{node:<14}: {node_offset:+.3f} sec")
        used.append(node_offset)

# Step 3: average offset
average = sum(used) / len(used)
print(f"\nAverage Offset: {average:+.3f} sec")

# Step 4: corrections
print("\n------------------------------------------\n")
print("Corrections\n")
corrections = {}
for node, node_offset in offsets.items():
    corrections[node] = average - node_offset
    print(f"{node:<14}: {corrections[node]:+.3f} sec")

# Step 5: send corrections to clients and apply the master's own correction
for host in CLIENTS:
    send(host, f"CORRECTION {corrections[host]}")
offset += corrections["Master"]

# Step 6: show final clocks
print("\n------------------------------------------\n")
print("Final Clocks\n")
show_clocks(poll_clocks(), with_error=True)
