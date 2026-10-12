import json
import math
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

offset = float(os.getenv("CLOCK_OFFSET", "0"))
client_id = os.getenv("CLIENT_ID", "client")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/clock", "/health"):
            self.send_error(404)
            return
        self.reply({"client": client_id, "clock": time.time() + offset})

    def do_POST(self):
        global offset
        if self.path != "/adjust":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError
            correction = float(json.loads(self.rfile.read(size))["correction"])
            if not math.isfinite(correction):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            self.send_error(400, "A finite numeric correction is required")
            return
        before = time.time() + offset
        offset += correction
        print(f"{client_id}: before={before:.6f}, correction={correction:+.6f}s, "
              f"after={time.time() + offset:.6f}", flush=True)
        self.reply({"client": client_id, "clock": time.time() + offset})

    def reply(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Berkeley {client_id}: initial offset={offset:+g}s", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
