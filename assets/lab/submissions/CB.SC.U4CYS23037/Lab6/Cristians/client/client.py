"""
Cristian's Clock Synchronization Algorithm - Client

Responsibilities:
1. Start with a configurable logical clock offset (CLOCK_OFFSET env var, seconds).
2. Record time (on its own, possibly skewed, logical clock) immediately before
   sending a request -> T1.
3. Send TIME_REQUEST to the master.
4. Receive the master's current (reference) time.
5. Record time (on its own logical clock) immediately after receiving -> T2.
6. Calculate RTT = T2 - T1.
7. Estimate one-way network delay = RTT / 2.
8. Calculate corrected clock = Master Time + RTT / 2.
9. Display the synchronization result and repeat every SYNC_INTERVAL seconds.
"""

import socket
import time
import os
import json
import datetime
import csv

MASTER_HOST = os.environ.get("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.environ.get("MASTER_PORT", 5000))
CLIENT_ID = os.environ.get("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", 0))       # seconds, simulated clock skew
SYNC_INTERVAL = float(os.environ.get("SYNC_INTERVAL", 10))    # seconds between syncs
SYNC_COUNT = int(os.environ.get("SYNC_COUNT", 0))             # 0 = run forever
RESULTS_FILE = os.environ.get("RESULTS_FILE", "")             # optional CSV output path


def local_clock():
    """
    The client's own (possibly skewed) logical clock.
    A constant offset simulates clock drift: the client 'thinks' it is
    CLOCK_OFFSET seconds ahead/behind the real reference time kept by the
    master. Because the offset is constant, it cancels out of RTT (a
    *duration* measurement) but not out of any single timestamp reading.
    """
    return time.time() + CLOCK_OFFSET


def fmt(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]


def sync_once(run_number: int):
    initial_clock = local_clock()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        sock.connect((MASTER_HOST, MASTER_PORT))

        # Step 1: record request time on the client's own clock
        t1 = local_clock()

        # Step 2: send request
        sock.sendall(b"TIME_REQUEST")

        # Step 3: receive master time
        raw = sock.recv(4096).decode()

        # Step 4: record response time on the client's own clock
        t2 = local_clock()

        response = json.loads(raw)
        master_time = response["master_time"]

        # Step 5: RTT
        rtt = t2 - t1

        # Step 6: one-way delay estimate
        est_delay = rtt / 2

        # Step 7: corrected/synchronized clock
        corrected_clock = master_time + est_delay

        # "Ground truth" comparison: the real, un-skewed wall clock at the
        # moment we finished. Cristian's algorithm should pull the client's
        # corrected clock very close to this.
        true_time_now = time.time()
        final_error = (corrected_clock - true_time_now) * 1000  # ms

        print("\n========== CRISTIAN'S ALGORITHM ==========")
        print(f"Client ID       : {CLIENT_ID}  (run #{run_number})")
        print(f"Configured Offset : {CLOCK_OFFSET:+.3f} s")
        print(f"Initial Clock   : {fmt(initial_clock)}")
        print()
        print(f"T1              : {fmt(t1)}")
        print(f"Master Time     : {fmt(master_time)}")
        print(f"T2              : {fmt(t2)}")
        print()
        print(f"RTT             : {rtt * 1000:.1f} ms")
        print(f"Estimated Delay : {est_delay * 1000:.1f} ms")
        print()
        print(f"Corrected Clock : {fmt(corrected_clock)}")
        print(f"Final Error     : {final_error:.2f} ms")
        print("============================================")

        if RESULTS_FILE:
            write_row(run_number, initial_clock, t1, master_time, t2, rtt, est_delay, corrected_clock, final_error)

        return dict(rtt_ms=rtt * 1000, delay_ms=est_delay * 1000, error_ms=final_error)

    except (ConnectionRefusedError, socket.timeout, socket.gaierror) as exc:
        # Part L, Q7: what happens if the master is unavailable
        print(f"[{CLIENT_ID}] Could not reach master ({MASTER_HOST}:{MASTER_PORT}): {exc}. "
              f"Keeping previous (uncorrected) clock and will retry.")
        return None
    finally:
        sock.close()


def write_row(run_number, initial_clock, t1, master_time, t2, rtt, delay, corrected, error):
    file_exists = os.path.isfile(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["run", "client", "initial_clock", "t1", "master_time", "t2",
                              "rtt_ms", "estimated_delay_ms", "corrected_clock", "final_error_ms"])
        writer.writerow([run_number, CLIENT_ID, fmt(initial_clock), fmt(t1), fmt(master_time), fmt(t2),
                          f"{rtt*1000:.1f}", f"{delay*1000:.1f}", fmt(corrected), f"{error:.2f}"])


def main():
    print(f"[{CLIENT_ID}] Starting. Offset={CLOCK_OFFSET:+.1f}s, "
          f"Master={MASTER_HOST}:{MASTER_PORT}, Interval={SYNC_INTERVAL}s")

    # Give the master a moment to come up first.
    time.sleep(3)

    run_number = 1
    while True:
        sync_once(run_number)
        if SYNC_COUNT and run_number >= SYNC_COUNT:
            break
        run_number += 1
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
