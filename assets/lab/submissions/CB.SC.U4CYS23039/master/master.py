"""
Lab 6A - Cristian's Algorithm : Master / Time Server

Responsibilities (Part C):
  - Start a TCP server and listen for client requests
  - Maintain its own logical clock (OS clock + MASTER_OFFSET)
  - Return the current logical time on TIME_REQUEST
  - Optionally introduce an artificial delay (Part J experiments)
  - Display every request received

Environment variables:
  PORT             listening port                    (default 5000)
  MASTER_OFFSET    master logical clock offset, s    (default 0)
  MASTER_DELAY_MS  artificial delay per request, ms  (default 0)
  DELAY_MODE       where the delay is applied        (default symmetric)
                     symmetric -> half before reading the clock, half after
                                  (models equal request/response delay)
                     request   -> all before reading the clock
                                  (models a slow request path)
                     response  -> all after reading the clock
                                  (models a slow response path)
"""

import os
import socketserver
import threading
import time
from datetime import datetime, timedelta, timezone

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))
MASTER_OFFSET = float(os.getenv("MASTER_OFFSET", "0"))
MASTER_DELAY_MS = float(os.getenv("MASTER_DELAY_MS", "0"))
DELAY_MODE = os.getenv("DELAY_MODE", "symmetric").strip().lower()

IST = timezone(timedelta(hours=5, minutes=30))
print_lock = threading.Lock()


def master_clock():
    """The master's logical clock (the OS clock is never modified)."""
    return time.time() + MASTER_OFFSET


def fmt(ts):
    """DD/MM/YYYY_HH:MM:SS:milliseconds, 24-hour, IST."""
    dt = datetime.fromtimestamp(ts, tz=IST)
    return dt.strftime("%d/%m/%Y_%H:%M:%S") + f":{dt.microsecond // 1000:03d}"


def split_delay():
    """Returns (seconds before reading clock, seconds after reading clock)."""
    total = MASTER_DELAY_MS / 1000.0
    if DELAY_MODE == "request":
        return total, 0.0
    if DELAY_MODE == "response":
        return 0.0, total
    return total / 2, total / 2  # symmetric


class TimeRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        raw = self.request.recv(1024).decode(errors="replace").strip()
        parts = raw.split("|", 1)
        client_id = parts[1] if len(parts) == 2 else f"{self.client_address[0]}"

        if parts[0] != "TIME_REQUEST":
            with print_lock:
                print(f"[MASTER] Ignored unknown message from {client_id}: {raw!r}", flush=True)
            return

        before, after = split_delay()
        if before:
            time.sleep(before)          # delay on the "request" side
        master_time = master_clock()    # timestamp taken here
        if after:
            time.sleep(after)           # delay on the "response" side

        self.request.sendall(f"MASTER_TIME={master_time!r}".encode())

        with print_lock:
            print(
                f"[MASTER] TIME_REQUEST from {client_id:<8} ({self.client_address[0]}) "
                f"-> MASTER_TIME = {fmt(master_time)}",
                flush=True,
            )


class ThreadedTimeServer(socketserver.ThreadingTCPServer):
    # One thread per client so simultaneous requests don't queue behind
    # each other (queueing would inflate RTT and skew the results).
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    if DELAY_MODE not in ("symmetric", "request", "response"):
        raise SystemExit(f"Invalid DELAY_MODE {DELAY_MODE!r}")

    print("=" * 60, flush=True)
    print(f"[MASTER] Time server listening on {HOST}:{PORT}", flush=True)
    print(f"[MASTER] Logical clock offset : {MASTER_OFFSET:+.3f} s", flush=True)
    print(f"[MASTER] Artificial delay     : {MASTER_DELAY_MS:.0f} ms ({DELAY_MODE})", flush=True)
    print(f"[MASTER] Current master time  : {fmt(master_clock())}", flush=True)
    print("=" * 60, flush=True)

    with ThreadedTimeServer((HOST, PORT), TimeRequestHandler) as server:
        server.serve_forever()
