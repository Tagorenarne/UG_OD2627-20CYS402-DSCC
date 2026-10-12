import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))

CLIENTS = [
    ("client1", 5001),
    ("client2", 5001),
    ("client3", 5001),
    ("client4", 5001)
]


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]


def get_clock(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((host, port))

            s.sendall(b"CLOCK_REQUEST\n")

            data = s.recv(1024).decode().strip()

            if data.startswith("CLOCK:"):
                return float(data.split(":")[1]), s

    except Exception as e:
        print(f"Could not contact {host}: {e}")

    return None, None


def send_correction(sock, correction):
    try:
        message = f"CORRECTION:{correction}\n"
        sock.sendall(message.encode())
    except Exception:
        pass


print("=" * 50)
print("        BERKELEY CLOCK SYNCHRONIZATION")
print("=" * 50)

print("\nWaiting for clients...")

time.sleep(5)

print("\nInitial Clocks")
print("-" * 50)

master_clock = logical_time()

print(f"Master       : {format_time(master_clock)}")

client_data = []

for hostname, port in CLIENTS:

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((hostname, port))

            s.sendall(b"CLOCK_REQUEST\n")

            data = s.recv(1024).decode().strip()

            if data.startswith("CLOCK:"):

                client_clock = float(data.split(":")[1])

                client_data.append({
                    "host": hostname,
                    "clock": client_clock,
                    "socket": s
                })

                print(f"{hostname:<12} : {format_time(client_clock)}")

    except Exception as e:
        print(f"{hostname:<12} : NO RESPONSE ({e})")


print("\n" + "-" * 50)
print("Clock Offsets")
print("-" * 50)

offsets = []

master_offset = 0.0

print(f"Master       : {master_offset:+.2f} sec")

for client in client_data:

    offset = client["clock"] - master_clock

    client["offset"] = offset

    offsets.append(offset)

    print(f"{client['host']:<12} : {offset:+.2f} sec")


# Include master in average
all_offsets = [master_offset] + offsets

if len(all_offsets) > 0:
    average_offset = sum(all_offsets) / len(all_offsets)
else:
    average_offset = 0


print("\nAverage Offset: " + f"{average_offset:+.2f} sec")


print("\n" + "-" * 50)
print("Corrections")
print("-" * 50)

master_correction = average_offset - master_offset

print(f"Master       : {master_correction:+.2f} sec")

# Send corrections to clients
for client in client_data:

    correction = average_offset - client["offset"]

    client["correction"] = correction

    print(f"{client['host']:<12} : {correction:+.2f} sec")

    try:
        # Reconnect to send correction
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((client["host"], 5001))

            s.sendall(b"CLOCK_REQUEST\n")

            s.recv(1024)

            message = f"CORRECTION:{correction}\n"
            s.sendall(message.encode())

    except Exception as e:
        print(f"Failed to send correction to {client['host']}: {e}")


# Apply correction to master's logical clock
CLOCK_OFFSET += master_correction

final_master_clock = master_clock + master_correction

print("\n" + "-" * 50)
print("Final Clocks")
print("-" * 50)

print(f"Master       : {format_time(final_master_clock)}")

for client in client_data:

    final_clock = client["clock"] + client["correction"]

    print(f"{client['host']:<12} : {format_time(final_clock)}")
