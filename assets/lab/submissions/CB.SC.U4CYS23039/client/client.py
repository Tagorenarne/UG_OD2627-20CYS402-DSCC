"""
Lab 6A - Cristian's Algorithm : Client

Each client keeps a LOGICAL clock = OS clock + offset. The OS clock is never
modified; "setting the clock" means changing the logical offset.

Algorithm (Part E):
  T1          = client time immediately before sending TIME_REQUEST
  MASTER_TIME = time returned by the master
  T2          = client time immediately after receiving the response
  RTT         = T2 - T1
  Delay       = RTT / 2              (assumes symmetric network delay)
  Corrected   = MASTER_TIME + RTT/2  -> becomes the client's new logical time

Final error (evaluation only):
  All containers share the host kernel's clock, so the master's true logical
  time at the instant T2 was taken is (OS time at T2 + MASTER_OFFSET).
  Final Error = Corrected Clock - true master time at T2
  (positive = client ahead of master, negative = client behind).
  The algorithm itself never uses this value.

Environment variables:
  CLIENT_ID        name shown in logs/results   (default client)
  CLOCK_OFFSET     initial logical offset, s    (default 0)
  MASTER_HOST      master hostname              (default clock-master)
  MASTER_PORT      master port                  (default 5000)
  SYNC_ROUNDS      synchronization rounds       (default 1)
  SYNC_INTERVAL    seconds between rounds       (default 5)
  EXPERIMENT       experiment number (labels)   (default 1)
  MASTER_DELAY_MS  master delay (labels only)   (default 0)
  DELAY_MODE       master delay mode (labels)   (default symmetric)
  MASTER_OFFSET    master offset (for error)    (default 0)
  RESULTS_DIR      where CSV results go         (default /results)
"""

import csv
import os
import socket
import time
from datetime import datetime, timedelta, timezone

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
MASTER_HOST = os.getenv("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.getenv("MASTER_PORT", "5000"))
SYNC_ROUNDS = int(os.getenv("SYNC_ROUNDS", "1"))
SYNC_INTERVAL = float(os.getenv("SYNC_INTERVAL", "5"))
EXPERIMENT = os.getenv("EXPERIMENT", "1")
MASTER_DELAY_MS = float(os.getenv("MASTER_DELAY_MS", "0"))
DELAY_MODE = os.getenv("DELAY_MODE", "symmetric")
MASTER_OFFSET = float(os.getenv("MASTER_OFFSET", "0"))
RESULTS_DIR = os.getenv("RESULTS_DIR", "/results")

IST = timezone(timedelta(hours=5, minutes=30))

CSV_FIELDS = [
    "experiment", "master_delay_ms", "delay_mode", "client", "round",
    "configured_offset_s", "initial_clock", "error_before_ms",
    "t1", "master_time", "t2", "rtt_ms", "estimated_delay_ms",
    "corrected_clock", "final_error_ms",
]


def fmt(ts):
    """DD/MM/YYYY_HH:MM:SS:milliseconds, 24-hour, IST."""
    dt = datetime.fromtimestamp(ts, tz=IST)
    return dt.strftime("%d/%m/%Y_%H:%M:%S") + f":{dt.microsecond // 1000:03d}"


class LogicalClock:
    """Logical clock layered on the OS clock; the OS clock is never touched."""

    def __init__(self, offset):
        self.offset = offset

    def now(self):
        return time.time() + self.offset

    def read(self):
        """Returns (logical time, underlying OS time) sampled together."""
        real = time.time()
        return real + self.offset, real

    def set_at(self, new_time, real_at):
        """Makes the clock read `new_time` at OS instant `real_at`."""
        self.offset = new_time - real_at


def request_master_time(clock):
    """Performs one Cristian exchange. Returns (T1, master_time, T2, real_T2)."""
    with socket.create_connection((MASTER_HOST, MASTER_PORT), timeout=10) as s:
        # Connection is already established, so T1..T2 covers only the
        # request/response exchange itself.
        T1 = clock.now()                                     # Step 1
        s.sendall(f"TIME_REQUEST|{CLIENT_ID}".encode())      # Step 2
        reply = s.recv(1024).decode()                        # Step 3
        T2, real_T2 = clock.read()                           # Step 4

    if not reply.startswith("MASTER_TIME="):
        raise ValueError(f"Unexpected reply from master: {reply!r}")
    master_time = float(reply.split("=", 1)[1])
    return T1, master_time, T2, real_T2


def synchronize(clock, round_no):
    initial_clock = clock.now()
    error_before_ms = (initial_clock - (time.time() + MASTER_OFFSET)) * 1000

    T1, master_time, T2, real_T2 = request_master_time(clock)

    rtt = T2 - T1                                   # Step 5
    est_delay = rtt / 2                             # Step 6
    corrected = master_time + est_delay             # Step 7
    clock.set_at(corrected, real_T2)                # adopt as new logical time

    true_master_at_T2 = real_T2 + MASTER_OFFSET
    final_error_ms = (corrected - true_master_at_T2) * 1000

    print(
        "\n".join([
            "",
            "========== CRISTIAN'S ALGORITHM ==========",
            "",
            f"Client ID       : {CLIENT_ID}",
            f"Experiment      : {EXPERIMENT} (master delay {MASTER_DELAY_MS:.0f} ms, {DELAY_MODE})",
            f"Round           : {round_no}/{SYNC_ROUNDS}",
            f"Initial Clock   : {fmt(initial_clock)}",
            f"Error Before    : {error_before_ms:+.3f} ms",
            "",
            f"T1              : {fmt(T1)}",
            f"Master Time     : {fmt(master_time)}",
            f"T2              : {fmt(T2)}",
            "",
            f"RTT             : {rtt * 1000:.3f} ms",
            f"Estimated Delay : {est_delay * 1000:.3f} ms",
            "",
            f"Corrected Clock : {fmt(corrected)}",
            f"Final Error     : {final_error_ms:+.3f} ms",
            "==========================================",
        ]),
        flush=True,
    )

    return {
        "experiment": EXPERIMENT,
        "master_delay_ms": f"{MASTER_DELAY_MS:.0f}",
        "delay_mode": DELAY_MODE,
        "client": CLIENT_ID,
        "round": round_no,
        "configured_offset_s": f"{CLOCK_OFFSET:+g}",
        "initial_clock": fmt(initial_clock),
        "error_before_ms": f"{error_before_ms:+.3f}",
        "t1": fmt(T1),
        "master_time": fmt(master_time),
        "t2": fmt(T2),
        "rtt_ms": f"{rtt * 1000:.3f}",
        "estimated_delay_ms": f"{est_delay * 1000:.3f}",
        "corrected_clock": fmt(corrected),
        "final_error_ms": f"{final_error_ms:+.3f}",
    }


def main():
    clock = LogicalClock(CLOCK_OFFSET)
    print(
        f"[{CLIENT_ID}] Started with logical clock offset {CLOCK_OFFSET:+g} s "
        f"-> {fmt(clock.now())}",
        flush=True,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, f"exp{EXPERIMENT}_{CLIENT_ID}.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for round_no in range(1, SYNC_ROUNDS + 1):
            for attempt in range(1, 11):
                try:
                    row = synchronize(clock, round_no)
                    writer.writerow(row)
                    f.flush()
                    break
                except (OSError, ValueError) as e:
                    # Master unavailable: the logical clock keeps running
                    # uncorrected, so we retry rather than crash.
                    print(f"[{CLIENT_ID}] Master unreachable (attempt {attempt}/10): {e}", flush=True)
                    time.sleep(2)
            else:
                print(f"[{CLIENT_ID}] Giving up: master unavailable, clock NOT synchronized.", flush=True)
                raise SystemExit(1)

            if round_no < SYNC_ROUNDS:
                time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
