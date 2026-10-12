"""
clock.py - Shared logical-clock and wire-protocol helpers.

Used by BOTH the leader (master/coordinator) and the followers (clients) so
that the two Docker images speak exactly the same protocol.

20CYS402 - Distributed Systems and Cloud Computing
Lab #6B - Berkeley Clock Synchronization Algorithm
"""

import json
import socket
import threading
import time

# ---------------------------------------------------------------------------
# Logical clock
# ---------------------------------------------------------------------------


def parse_base_time(text):
    """
    Parse 'HH:MM:SS(.sss)' into seconds since midnight (43200 == 12:00:00).
    The special value 'auto' means "use the real time of day right now", which
    is what a machine with a real (but wrong) hardware clock would show.
    """
    text = str(text).strip()
    if text.lower() == "auto":
        return time.time() % 86400.0
    try:
        parts = text.split(":")
        if len(parts) != 3:
            raise ValueError
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except (ValueError, TypeError):
        return float(text)


class LogicalClock:
    """
    A free-running logical clock that ticks at the *same rate* on every node
    but is shifted by a fixed `offset` seconds.  The fixed offset is the clock
    error that Berkeley's algorithm has to remove.

    Two modes:

    'frozen'  (default - reproduces the hand-out exactly)
        clock = BASE_TIME + offset + ticks * TICK_STEP
        `ticks` is driven by the round number sent in the request, so every
        node advances in perfect lock-step and the measured offsets are
        exactly the configured ones, no matter when each container booted.
        Set CLOCK_TICK=0 for a completely frozen clock (12:00:00 + offset).

    'running'  (realistic hardware-clock model)
        clock = BASE_TIME + offset + (monotonic time since boot)
        With CLOCK_BASE=auto this is literally "the machine's clock is set
        `offset` seconds wrong", which is the real-world problem.
    """

    def __init__(self, offset=0.0, base_time="12:00:00", mode="frozen", tick=0.5):
        self.base_time = parse_base_time(base_time)
        self.offset = float(offset)
        self.mode = str(mode).strip().lower()
        self.tick = float(tick)
        self._t0 = time.monotonic()
        self._ticks = 0.0
        self._lock = threading.Lock()

    # -- reading -------------------------------------------------------------
    def now(self):
        if self.mode == "running":
            return self.base_time + self.offset + (time.monotonic() - self._t0)
        return self.base_time + self.offset + self._ticks

    def skew(self):
        """How far this clock is from the reference it is compared against."""
        return self.offset

    # -- driving (frozen mode only) -------------------------------------------
    def set_ticks(self, index):
        """
        Move the logical clock to step `index`.  Both the master (at the start
        of a round) and the clients (on CLOCK_REQUEST) call this with the same
        round number, so all clocks stay in lock-step.
        """
        if self.mode == "running":
            return self.now()
        with self._lock:
            self._ticks = max(self._ticks, float(index) * self.tick)
        return self.now()

    # -- correction ----------------------------------------------------------
    def apply_correction(self, correction):
        """Shift the clock by `correction` seconds and return the new offset."""
        with self._lock:
            self.offset = float(self.offset) + float(correction)
            return self.offset


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def fmt_clock(seconds, decimals=1):
    """43200.8 -> '12:00:00.8'   (decimals=0 -> '12:00:00')"""
    if seconds is None:
        return "n/a"
    value = round(float(seconds), decimals)
    sign = "-" if value < 0 else ""
    value = abs(value)
    hours = int(value // 3600) % 24
    minutes = int((value % 3600) // 60)
    secs = value % 60
    if decimals == 0:
        return f"{sign}{hours:02d}:{minutes:02d}:{int(secs):02d}"
    return f"{sign}{hours:02d}:{minutes:02d}:{secs:0{decimals + 3}.{decimals}f}"


def fmt_signed(value, decimals=1):
    """8.0 -> '+8.0'   (always shows the sign, like the lab hand-out).

    Rounds first and collapses negative zero, so a value that is mathematically
    zero never prints as '-0.0' in the report tables.
    """
    if value is None:
        return "n/a"
    value = round(float(value), decimals)
    if value == 0:
        value = 0.0
    return f"{value:+.{decimals}f}"


# ---------------------------------------------------------------------------
# Line-delimited JSON wire protocol
# ---------------------------------------------------------------------------
#
#   LEADER   -> FOLLOWER : {"cmd": "CLOCK_REQUEST", "round": 1}
#   FOLLOWER -> LEADER   : {"cmd": "CLOCK_RESPONSE", "clock": 43192.0, ...}
#   LEADER   -> FOLLOWER : {"cmd": "CLOCK_SET", "correction": 8.8, ...}
#   FOLLOWER -> LEADER   : {"cmd": "CLOCK_ACK", "clock": 43200.8, ...}
#   LEADER   -> FOLLOWER : {"cmd": "CLOCK_VERIFY", "round": 1}
#   FOLLOWER -> LEADER   : {"cmd": "CLOCK_VERIFY_RESPONSE", "clock": ...}
#   LEADER   -> FOLLOWER : {"cmd": "PING"}  ->  {"cmd": "PONG"}
#
# Every message is one JSON object terminated by a newline.

ENCODING = "utf-8"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 5.0


def send_message(sock, payload):
    data = (json.dumps(payload) + "\n").encode(ENCODING)
    sock.sendall(data)


def recv_message(sock, timeout=DEFAULT_TIMEOUT):
    """Read exactly one newline-terminated JSON object from the socket."""
    sock.settimeout(timeout)
    buffer = b""
    while b"\n" not in buffer:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            raise TimeoutError("timed out waiting for a reply")
        if not chunk:
            break
        buffer += chunk
    if not buffer.strip():
        raise ConnectionError("peer closed the connection without replying")
    return json.loads(buffer.decode(ENCODING).strip())


def rpc(host, port, payload, timeout=DEFAULT_TIMEOUT):
    """One-shot request/response against a follower container."""
    with socket.create_connection((host, port), timeout=timeout) as sock:
        send_message(sock, payload)
        return recv_message(sock, timeout=timeout)


def split_node_spec(spec, default_port=DEFAULT_PORT):
    """'client1:5000' -> ('client1', 5000);  'client1' -> ('client1', 5000)"""
    spec = str(spec).strip()
    if not spec:
        return None
    if ":" in spec:
        host, _, port = spec.rpartition(":")
        try:
            return host, int(port)
        except ValueError:
            return spec, default_port
    return spec, default_port
