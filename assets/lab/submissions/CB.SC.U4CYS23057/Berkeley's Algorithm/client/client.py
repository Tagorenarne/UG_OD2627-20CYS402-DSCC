import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

CLIENT_ID = os.getenv("CLIENT_ID", "client")
offset = float(os.getenv("CLOCK_OFFSET", "0"))  # seconds away from real time


def clock():
    # Logical clock = real time + offset
    return time.time() + offset


def fmt(t):
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int(t % 1 * 1000):03d}"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global offset
        url = urlparse(self.path)

        if url.path == "/time":  # CLOCK_REQUEST from master
            t = clock()
            print(f"[{CLIENT_ID}] CLOCK_REQUEST received, sending {fmt(t)}")
            reply = str(t)

        elif url.path == "/adjust":  # correction from master
            c = float(parse_qs(url.query)["correction"][0])
            before = clock()
            offset += c
            print(f"[{CLIENT_ID}] correction {c:+.3f} sec | before {fmt(before)} | after {fmt(clock())}")
            reply = "OK"

        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(reply.encode())

    def log_message(self, *args):  # silence default HTTP logs
        pass


print(f"[{CLIENT_ID}] started, clock = {fmt(clock())} (offset {offset:+.1f} sec)")
HTTPServer(("", 8080), Handler).serve_forever()
