"""Berkeley algorithm - client node.
Keeps a logical clock (real time + configurable offset), answers the master's
CLOCK_REQUEST and applies the CORRECTION it receives."""
import json, os, socket, threading, time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
PORT = int(os.getenv("PORT", "5000"))


def fmt(ts):
    return time.strftime("%H:%M:%S", time.gmtime(ts)) + f"{ts % 1:.3f}"[1:]


class LogicalClock:
    def __init__(self, offset):
        self.offset = offset
        self.lock = threading.Lock()

    def now(self):
        with self.lock:
            return time.time() + self.offset

    def adjust(self, delta):
        with self.lock:
            self.offset += delta


clock = LogicalClock(CLOCK_OFFSET)


def handle(conn, addr):
    with conn, conn.makefile("rw") as f:
        for line in f:
            msg = json.loads(line)
            if msg["type"] == "CLOCK_REQUEST":
                t = clock.now()
                print(f"[{CLIENT_ID}] CLOCK_REQUEST from {addr[0]} -> replying {fmt(t)}", flush=True)
                reply = {"type": "CLOCK_REPLY", "id": CLIENT_ID, "clock": t}
            elif msg["type"] == "CORRECTION":
                before = clock.now()
                clock.adjust(msg["value"])
                after = clock.now()
                print(f"[{CLIENT_ID}] CORRECTION {msg['value']:+.3f}s  before={fmt(before)}  after={fmt(after)}", flush=True)
                reply = {"type": "ACK", "id": CLIENT_ID, "clock": after}
            else:
                reply = {"type": "ERROR"}
            f.write(json.dumps(reply) + "\n")
            f.flush()


def main():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen()
    print(f"[{CLIENT_ID}] started, initial offset {CLOCK_OFFSET:+.1f}s, clock={fmt(clock.now())}", flush=True)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
