import socket
import time
import os
from datetime import datetime

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


def synchronize():

    t1 = logical_time()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((MASTER_HOST, MASTER_PORT))

    client_socket.send(b"TIME_REQUEST")

    data = client_socket.recv(1024)

    t2 = logical_time()

    master_time = float(data.decode())

    client_socket.close()

    rtt = t2 - t1

    estimated_delay = rtt / 2

    corrected_time = master_time + estimated_delay

    final_error = final_error = abs(corrected_time - master_time)

    print("\n========== CRISTIAN'S ALGORITHM ==========")

    print("Client ID       :", CLIENT_ID)
    print("Initial Clock   :", format_time(t1))

    print("T1              :", format_time(t1))
    print("Master Time     :", format_time(master_time))
    print("T2              :", format_time(t2))

    print("RTT             :", round(rtt * 1000, 2), "ms")
    print("Estimated Delay :", round(estimated_delay * 1000, 2), "ms")

    print("Corrected Clock :", format_time(corrected_time))
    print("Final Error     :", round(final_error * 1000, 2), "ms")


if __name__ == "__main__":
    synchronize()