#!/usr/bin/env python3
"""
client.py - Berkeley Clock Synchronization :: FOLLOWER / CLIENT
==============================================================
20CYS402 - Distributed Systems and Cloud Computing
Lab #6B - Berkeley Clock Synchronization Algorithm

Each follower runs a small TCP server and waits to be contacted by the
coordinator.  It never contacts anybody first.

    1. Boot with a configurable clock offset (e.g. CLOCK_OFFSET=-8)
    2. Keep a free-running logical clock
    3. Answer  CLOCK_REQUEST  with the current clock value
    4. Receive CLOCK_SET and apply the correction
    5. Print the clock before and after synchronisation

Environment variables
---------------------
    CLIENT_ID       label for this node                     (client1)
    CLOCK_OFFSET    initial clock error in seconds          (-8)
    CLOCK_BASE      logical start time, 'HH:MM:SS'|'auto'   (12:00:00)
    CLOCK_MODE      'frozen' (lock-step demo) | 'running'   (frozen)
    CLOCK_TICK      seconds added per round in frozen mode  (0.5)
    PORT            TCP port to listen on                   (5000)
    SYNC_SERVERS    'host:port' list to print on boot       (informational)
"""

import os
import signal
import socketserver
import sys
import threading

from clock import (
    DEFAULT_PORT,
    LogicalClock,
    fmt_clock,
    fmt_signed,
    recv_message,
    send_message,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def env(name, default):
    value = os.environ.get(name)
    return default if value is None or value == "" else value


def env_float(name, default):
    try:
        return float(env(name, default))
    except (TypeError, ValueError):
        return default


def env_int(name, default):
    try:
        return int(env(name, default))
    except (TypeError, ValueError):
        return default


CLIENT_ID = env("CLIENT_ID", os.environ.get("NODE_ID", "client"))
CLOCK_OFFSET = env_float("CLOCK_OFFSET", 0.0)
CLOCK_BASE = env("CLOCK_BASE", "12:00:00")
CLOCK_MODE = env("CLOCK_MODE", "frozen")
CLOCK_TICK = env_float("CLOCK_TICK", 0.5)
PORT = env_int("PORT", DEFAULT_PORT)
SYNC_SERVERS = env("SYNC_SERVERS", "")

CLOCK = LogicalClock(
    offset=CLOCK_OFFSET, base_time=CLOCK_BASE,
    mode=CLOCK_MODE, tick=CLOCK_TICK,
)
STATE_LOCK = threading.Lock()

INITIAL_CLOCK = CLOCK.now()
CORRECTIONS = []
STOP = threading.Event()
SERVER = None

LINE = "=" * 70


def log(message):
    print(f"[{CLIENT_ID}] {message}", flush=True)


# ---------------------------------------------------------------------------
# Request handlers
# ---------------------------------------------------------------------------


def handle_clock_request(message):
    """Step 3 of the hand-out: report this node's current clock."""
    round_no = int(message.get("round", 0))
    with STATE_LOCK:
        # In frozen mode the clock is moved to the round the master is on, so
        # every node reads its clock at exactly the same logical instant.
        value = CLOCK.set_ticks(round_no)
        offset = CLOCK.offset
    return {
        "cmd": "CLOCK_RESPONSE",
        "node": CLIENT_ID,
        "round": round_no,
        "clock": value,
        "offset": offset,
        "pid": os.getpid(),
    }


def handle_clock_set(message):
    """Step 6 of the hand-out: apply the coordinator's correction."""
    correction = float(message["correction"])
    round_no = int(message.get("round", 0))
    with STATE_LOCK:
        before = CLOCK.now()
        CLOCK.apply_correction(correction)
        after = CLOCK.now()
    CORRECTIONS.append(
        {"round": round_no, "correction": correction,
         "before": before, "after": after}
    )
    log(f"round {round_no}: correction {fmt_signed(correction)} sec  "
        f"{fmt_clock(before)}  =>  {fmt_clock(after)}")
    return {
        "cmd": "CLOCK_ACK",
        "node": CLIENT_ID,
        "round": round_no,
        "correction": correction,
        "clock": after,
        "offset": CLOCK.offset,
    }


def handle_clock_verify(message):
    with STATE_LOCK:
        value = CLOCK.now()
    return {
        "cmd": "CLOCK_VERIFY_RESPONSE",
        "node": CLIENT_ID,
        "round": message.get("round", 0),
        "clock": value,
        "offset": CLOCK.offset,
    }


def handle_ping(_message):
    return {"cmd": "PONG", "node": CLIENT_ID, "clock": CLOCK.now()}


HANDLERS = {
    "CLOCK_REQUEST": handle_clock_request,
    "CLOCK_SET": handle_clock_set,
    "CLOCK_VERIFY": handle_clock_verify,
    "PING": handle_ping,
}


# ---------------------------------------------------------------------------
# TCP server
# ---------------------------------------------------------------------------


class Handler(socketserver.StreamRequestHandler):
    timeout = 30

    def handle(self):
        peer = f"{self.client_address[0]}:{self.client_address[1]}"
        try:
            message = recv_message(self.request, timeout=self.timeout)
        except (ConnectionError, ValueError):
            # Empty connect-then-close (e.g. a TCP health check) - not an error.
            return
        except (OSError, TimeoutError) as exc:
            log(f"bad request from {peer}: {exc}")
            return

        command = message.get("cmd")
        handler = HANDLERS.get(command)
        if handler is None:
            log(f"unknown command {command!r} from {peer}")
            reply = {"cmd": "ERROR", "error": f"unknown command {command!r}"}
        else:
            try:
                reply = handler(message)
            except Exception as exc:  # never let one bad message kill the node
                log(f"error handling {command}: {exc}")
                reply = {"cmd": "ERROR", "error": str(exc)}

        try:
            send_message(self.request, reply)
        except OSError:
            pass  # peer already gone - nothing to do


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def _handle_signal(signum, _frame):
    log(f"signal {signum} received - stopping")
    STOP.set()
    if SERVER is not None:
        threading.Thread(target=SERVER.shutdown, daemon=True).start()


def main():
    global SERVER
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    print(LINE, flush=True)
    print(f"  FOLLOWER NODE  {CLIENT_ID.upper()}  -  Berkeley clock participant",
          flush=True)
    print(LINE, flush=True)
    log(f"initial clock     : {fmt_clock(INITIAL_CLOCK)}")
    log(f"configured offset : {fmt_signed(CLOCK_OFFSET)} sec")
    log(f"clock mode        : {CLOCK_MODE}  (base {CLOCK_BASE}, "
        f"tick {CLOCK_TICK:g}s/round)")
    log(f"listening on      : 0.0.0.0:{PORT}")
    if SYNC_SERVERS:
        log(f"coordinator       : {SYNC_SERVERS}")
    log("waiting for CLOCK_REQUEST from the master ...")

    SERVER = ThreadedTCPServer(("0.0.0.0", PORT), Handler)
    try:
        SERVER.serve_forever(poll_interval=0.5)
    finally:
        SERVER.server_close()

    log("stopped")
    if CORRECTIONS:
        log("corrections applied this session:")
        for item in CORRECTIONS:
            log(f"   round {item['round']}: {fmt_signed(item['correction'])} sec   "
                f"{fmt_clock(item['before'])} -> {fmt_clock(item['after'])}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
