import socket
import datetime
import time
import os

SERVER_HOST = "clock-master"
SERVER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "Client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_logical_time():
    return datetime.datetime.now() + datetime.timedelta(seconds=CLOCK_OFFSET)


def synchronize_time():
    print("\n========== CRISTIAN'S ALGORITHM ==========")
    print(f"Client ID       : {CLIENT_ID}")
    print(f"Initial Clock   : {get_logical_time()}")

    for attempt in range(10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            T1 = time.perf_counter()
            T1_clock = get_logical_time()

            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.sendall(b"TIME_REQUEST")

            data = sock.recv(1024)

            T2 = time.perf_counter()
            T2_clock = get_logical_time()

            sock.close()
            break

        except (ConnectionRefusedError, socket.timeout):
            sock.close()
            print("Waiting for master server...")
            time.sleep(1)

    else:
        print("Could not connect to master server.")
        return

    response = data.decode()
    master_time = datetime.datetime.fromisoformat(
        response.split("=", 1)[1].strip()
    )

    rtt = T2 - T1
    estimated_delay = rtt / 2

    corrected_clock = master_time + datetime.timedelta(
        seconds=estimated_delay
    )

    actual_time = datetime.datetime.now()

    final_error = (
        corrected_clock - actual_time
    ).total_seconds()

    print(f"T1              : {T1_clock}")
    print(f"Master Time     : {master_time}")
    print(f"T2              : {T2_clock}")
    print(f"RTT             : {rtt * 1000:.3f} ms")
    print(f"Estimated Delay : {estimated_delay * 1000:.3f} ms")
    print(f"Corrected Clock : {corrected_clock}")
    print(f"Final Error     : {final_error * 1000:.3f} ms")
    print("==========================================\n")


if __name__ == "__main__":
    synchronize_time()