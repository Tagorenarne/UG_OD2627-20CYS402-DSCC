import json
import os
import socketserver
import threading
import time
from datetime import datetime, timezone

NODE_NAME = os.environ.get("CLIENT_ID", "client")
LISTEN_PORT = int(os.environ.get("PORT", "6000"))
START_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))

_mutex = threading.Lock()
time_difference = START_OFFSET  


def get_clock() -> float:
    with _mutex:
        return time.time() + time_difference


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global time_difference
        request_line = self.rfile.readline().decode().strip()
        if not request_line:
            return
        try:
            request_data = json.loads(request_line)
        except json.JSONDecodeError:
            return

        command = request_data.get("cmd")

        if command == "CLOCK_REQUEST": #checking if master asks for current clock
            reply = {"client_id": NODE_NAME, "time": get_clock()} #creating clock response
            print(f"[{NODE_NAME}] CLOCK_REQUEST -> {format_time(reply['time'])}", flush=True)
            self.wfile.write((json.dumps(reply) + "\n").encode()) # sennds response back to master

        elif command == "CORRECTION": #master sends correction to client
            adjustment = float(request_data.get("value", 0))
            previous_time = get_clock()
            with _mutex:
                time_difference += adjustment
            updated_time = get_clock()
            print(
                f"[{NODE_NAME}] Applying correction {adjustment:+.3f}s | "
                f"before={format_time(previous_time)} after={format_time(updated_time)}",
                flush=True,
            )
            self.wfile.write((json.dumps({"status": "ok"}) + "\n").encode())

        else:
            self.wfile.write((json.dumps({"error": "unknown command"}) + "\n").encode())


def main():
    print(
        f"[{NODE_NAME}] Starting. Initial offset={START_OFFSET:+.2f}s "
        f"Initial clock={format_time(get_clock())} listening on 0.0.0.0:{LISTEN_PORT}",
        flush=True,
    )
    server = socketserver.ThreadingTCPServer(("0.0.0.0", LISTEN_PORT), RequestHandler)
    server.allow_reuse_address = True
    server.serve_forever()


if __name__ == "__main__":
    main()
