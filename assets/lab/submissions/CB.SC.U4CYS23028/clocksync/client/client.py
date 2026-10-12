import socket
import time
import os
import datetime


MASTER_HOST = os.environ.get("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.environ.get("MASTER_PORT", "5000"))

CLIENT_ID = os.environ.get("CLIENT_ID", "client")

# Configurable initial offset (seconds) applied to this client's
# logical clock, e.g. CLOCK_OFFSET=-8 means the client's clock starts
# 8 seconds behind real time.
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))

# How many times to sync, and how long to wait between syncs.
SYNC_ROUNDS = int(os.environ.get("SYNC_ROUNDS", "1"))
SYNC_INTERVAL = float(os.environ.get("SYNC_INTERVAL", "5"))


def local_logical_time():
    """This client's own (uncorrected) clock: real time shifted by the
    configured offset."""
    return datetime.datetime.now() + datetime.timedelta(seconds=CLOCK_OFFSET)


def sync_once(round_num):

    initial_clock = local_logical_time()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Step 1 — record request time
    t1 = local_logical_time()

    s.connect((MASTER_HOST, MASTER_PORT))

    # Step 2 — send request
    s.send(b"TIME_REQUEST")

    # Step 3 — receive master time
    data = s.recv(1024).decode()
    s.close()

    if not data.startswith("MASTER_TIME="):
        raise ValueError(f"Unexpected response from master: {data}")

    master_time = datetime.datetime.fromisoformat(data[len("MASTER_TIME="):])

    # Step 4 — record response time
    t2 = local_logical_time()

    # Step 5 — calculate RTT
    rtt = (t2 - t1).total_seconds()

    # Step 6 — estimate one-way network delay
    estimated_delay = rtt / 2

    # Step 7 — calculate synchronized time
    corrected_clock = master_time + datetime.timedelta(seconds=estimated_delay)

    # Final synchronization error: how far the corrected clock still
    # differs from true wall-clock time. This should be close to 0,
    # showing the offset has been corrected away (unlike the client's
    # original offset, which was several seconds off).
    true_time_now = datetime.datetime.now()
    final_error = (corrected_clock - true_time_now).total_seconds()

    print("========== CRISTIAN'S ALGORITHM ==========\n")
    print(f"Client ID       : {CLIENT_ID} (round {round_num})")
    print(f"Initial Clock   : {initial_clock.time()}\n")
    print(f"T1              : {t1.time()}")
    print(f"Master Time     : {master_time.time()}")
    print(f"T2              : {t2.time()}\n")
    print(f"RTT             : {rtt * 1000:.0f} ms")
    print(f"Estimated Delay : {estimated_delay * 1000:.0f} ms\n")
    print(f"Corrected Clock : {corrected_clock.time()}")
    print(f"Final Error     : {final_error * 1000:.0f} ms")
    print("============================================\n")


def run():
    print(f"[{CLIENT_ID}] Starting with clock offset {CLOCK_OFFSET:+.1f}s, "
          f"connecting to {MASTER_HOST}:{MASTER_PORT}\n")

    for round_num in range(1, SYNC_ROUNDS + 1):
        try:
            sync_once(round_num)
        except (ConnectionRefusedError, OSError, ValueError) as e:
            print(f"[{CLIENT_ID}] round {round_num} failed: {e}")

        if round_num < SYNC_ROUNDS:
            time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    run()