import socket
import time
import os

PORT = 5000

CLIENTS = [
    ("clock-client1", 5001),
    ("clock-client2", 5002),
    ("clock-client3", 5003),
    ("clock-client4", 5004)
]

OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + OFFSET


def format_time(t):
    return time.strftime("%H:%M:%S", time.localtime(t)) + \
           f".{int((t % 1) * 10)}"


def main():

    master_time = get_time()

    clocks = {"Master": master_time}

    # Get time from clients
    for host, port in CLIENTS:

        s = socket.socket()
        s.connect((host, port))

        s.send(b"CLOCK_REQUEST")

        client_time = float(s.recv(1024).decode())

        s.close()

        clocks[host] = client_time

    # Calculate offsets
    offsets = {"Master": 0}

    for host in CLIENTS:
        offsets[host[0]] = clocks[host[0]] - master_time

    # Average offset
    average = sum(offsets.values()) / len(offsets)

    # Corrections
    corrections = {}

    for node in offsets:
        corrections[node] = average - offsets[node]

    # Send corrections
    for host, port in CLIENTS:

        s = socket.socket()
        s.connect((host, port))

        s.send(
            f"CORRECTION:{corrections[host]}".encode()
        )

        s.close()

    # Final clocks
    final = {}

    for node in clocks:
        final[node] = clocks[node] + corrections[node]

    # ---------- OUTPUT ----------

    print("\n========== BERKELEY ALGORITHM ==========\n")

    print("Initial Clocks\n")

    print("Master       :", format_time(clocks["Master"]))
    print("Client 1     :", format_time(clocks["clock-client1"]))
    print("Client 2     :", format_time(clocks["clock-client2"]))
    print("Client 3     :", format_time(clocks["clock-client3"]))
    print("Client 4     :", format_time(clocks["clock-client4"]))

    print("\n------------------------------------------\n")

    print("Clock Offsets\n")

    print("Master       : +0 sec")
    print("Client 1     :", f"{offsets['clock-client1']:+.0f} sec")
    print("Client 2     :", f"{offsets['clock-client2']:+.0f} sec")
    print("Client 3     :", f"{offsets['clock-client3']:+.0f} sec")
    print("Client 4     :", f"{offsets['clock-client4']:+.0f} sec")

    print("\nAverage Offset:", f"{average:+.1f}", "sec")

    print("\n------------------------------------------\n")

    print("Corrections\n")

    print("Master       :", f"{corrections['Master']:+.1f}", "sec")
    print("Client 1     :", f"{corrections['clock-client1']:+.1f}", "sec")
    print("Client 2     :", f"{corrections['clock-client2']:+.1f}", "sec")
    print("Client 3     :", f"{corrections['clock-client3']:+.1f}", "sec")
    print("Client 4     :", f"{corrections['clock-client4']:+.1f}", "sec")

    print("\n------------------------------------------\n")

    print("Final Clocks\n")

    print("Master       :", format_time(final["Master"]))
    print("Client 1     :", format_time(final["clock-client1"]))
    print("Client 2     :", format_time(final["clock-client2"]))
    print("Client 3     :", format_time(final["clock-client3"]))
    print("Client 4     :", format_time(final["clock-client4"]))


if __name__ == "__main__":
    main()