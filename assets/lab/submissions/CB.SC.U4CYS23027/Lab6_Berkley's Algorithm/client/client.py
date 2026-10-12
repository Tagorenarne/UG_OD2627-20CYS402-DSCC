import json
import os
import socketserver
import threading
import time
from datetime import datetime, timezone

CLIENT_ID = os.environ.get("CLIENT_ID", "client")
PORT = int(os.environ.get("PORT", "6000"))
INITIAL_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))

_lock = threading.Lock()
clock_offset = INITIAL_OFFSET  


def current_clock() -> float:
    with _lock:
        return time.time() + clock_offset


def fmt(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        global clock_offset
        line = self.rfile.readline().decode().strip()
        if not line:
            return
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return

        cmd = msg.get("cmd")

        if cmd == "CLOCK_REQUEST": #checking if master asks for current clock
            reply = {"client_id": CLIENT_ID, "time": current_clock()} #creating clock response
            print(f"[{CLIENT_ID}] CLOCK_REQUEST -> {fmt(reply['time'])}", flush=True)
            self.wfile.write((json.dumps(reply) + "\n").encode()) # sennds response back to master

        elif cmd == "CORRECTION": #master sends correction to client
            correction = float(msg.get("value", 0))
            before = current_clock()
            with _lock:
                clock_offset += correction
            after = current_clock()
            print(
                f"[{CLIENT_ID}] Applying correction {correction:+.3f}s | "
                f"before={fmt(before)} after={fmt(after)}",
                flush=True,
            )
            self.wfile.write((json.dumps({"status": "ok"}) + "\n").encode())

        else:
            self.wfile.write((json.dumps({"error": "unknown command"}) + "\n").encode())


def main():
    print(
        f"[{CLIENT_ID}] Starting. Initial offset={INITIAL_OFFSET:+.2f}s "
        f"Initial clock={fmt(current_clock())} listening on 0.0.0.0:{PORT}",
        flush=True,
    )
    server = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler)
    server.allow_reuse_address = True
    server.serve_forever()


if __name__ == "__main__":
    main()
