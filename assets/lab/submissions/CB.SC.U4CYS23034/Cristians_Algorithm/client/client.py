import os
import socket
import time
from datetime import datetime


def main():
    name = os.getenv("CLIENT_ID", "Client")
    offset = float(os.getenv("CLOCK_OFFSET", "0"))
    host = os.getenv("SERVER_HOST", "server")

    for attempt in range(30):
        try:
            client = socket.create_connection((host, 5000), timeout=15)
            break
        except OSError:
            time.sleep(0.2)
    else:
        raise ConnectionError("Could not connect to the time server")

    with client:
        t1 = time.time() + offset
        start = time.monotonic()
        client.sendall(b"TIME\n")
        with client.makefile("r") as stream:
            reply = stream.readline()
        rtt = time.monotonic() - start
        received_at = time.time()
        t2 = received_at + offset

    server_time, server_offset = map(float, reply.split())
    corrected = server_time + rtt / 2
    adjustment = corrected - t2
    offset += adjustment
    error = abs((received_at + offset) - (received_at + server_offset))

    print(f"\n{name} - Cristian's algorithm")
    for label, value in (("Initial clock", t1), ("T1", t1), ("Server time", server_time),
                         ("T2", t2), ("Corrected clock", corrected)):
        print(f"{label:<17}: {datetime.fromtimestamp(value).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"RTT              : {rtt * 1000:.3f} ms")
    print(f"Estimated delay  : {rtt * 500:.3f} ms")
    print(f"Clock adjustment : {adjustment:+.6f} seconds")
    print(f"Final error      : {error * 1000:.3f} ms")


if __name__ == "__main__":
    main()
