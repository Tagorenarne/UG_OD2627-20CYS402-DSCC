import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
PROCESSING_DELAY = float(os.getenv("PROCESSING_DELAY_MS", "0")) / 1000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            payload = {"status": "ready"}
        elif url.path == "/time":
            try:
                delay = float(parse_qs(url.query).get("delay_ms", ["0"])[0])
                if not 0 <= delay <= 5000:
                    raise ValueError
            except ValueError:
                self.send_error(400, "delay_ms must be between 0 and 5000")
                return
            # Simulate equal request and response delays around the timestamp.
            time.sleep(delay / 2000 + PROCESSING_DELAY)
            payload = {"master_time": time.time() + OFFSET, "master_offset": OFFSET}
            time.sleep(delay / 2000)
            print(f"TIME_REQUEST: client={self.client_address[0]}, delay={delay} ms", flush=True)
        else:
            self.send_error(404)
            return
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Cristian time server: port=5000, offset={OFFSET:+g}s", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
