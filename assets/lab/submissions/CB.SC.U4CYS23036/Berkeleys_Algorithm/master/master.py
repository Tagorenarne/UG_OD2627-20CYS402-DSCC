import json
import math
import os
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def calculate_corrections(offsets, threshold=None):
    included = {node: value for node, value in offsets.items()
                if node == "master" or threshold is None or abs(value) <= threshold}
    average = sum(included.values()) / len(included)
    return average, {node: average - value for node, value in offsets.items()}, included


def request(host, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    call = Request(f"http://{host}:5000{path}", data=body,
                   headers={"Content-Type": "application/json"})
    with urlopen(call, timeout=10) as response:
        return json.load(response)


def clock_text(value):
    return datetime.fromtimestamp(value, timezone.utc).strftime("%H:%M:%S.%f")[:-3]


def main():
    master_offset = float(os.getenv("CLOCK_OFFSET", "0"))
    clients = os.getenv("CLIENTS", "client1,client2,client3,client4").split(",")
    limit = os.getenv("OUTLIER_THRESHOLD", "").strip()
    threshold = float(limit) if limit else None
    if threshold is not None and (not math.isfinite(threshold) or threshold < 0):
        raise ValueError("OUTLIER_THRESHOLD must be finite and nonnegative")
    initial = {"master": time.time() + master_offset}
    offsets = {"master": 0.0}
    for client in clients:
        start = time.time() + master_offset
        remote = request(client, "/clock")["clock"]
        end = time.time() + master_offset
        initial[client] = remote
        # Compare at the midpoint of the poll to account for elapsed time.
        offsets[client] = remote - (start + end) / 2
    average, corrections, included = calculate_corrections(offsets, threshold)
    print("BERKELEY CLOCK SYNCHRONIZATION")
    print(f"Average Offset: {average:+.6f}s; nodes in average: {', '.join(included)}")
    for client in clients:
        request(client, "/adjust", {"correction": corrections[client]})
    master_offset += corrections["master"]
    final = {"master": time.time() + master_offset}
    errors = {"master": 0.0}
    for client in clients:
        start = time.time() + master_offset
        final[client] = request(client, "/clock")["clock"]
        end = time.time() + master_offset
        errors[client] = (final[client] - (start + end) / 2) * 1000
    print(f"{'Node':<10} {'Initial':<14} {'Offset(s)':>11} {'Correction(s)':>14} {'Final':<14} {'Error(ms)':>10}")
    for node in offsets:
        print(f"{node:<10} {clock_text(initial[node]):<14} {offsets[node]:>+11.6f} "
              f"{corrections[node]:>+14.6f} {clock_text(final[node]):<14} {errors[node]:>+10.3f}")
    print("RESULT " + json.dumps({"initial": initial, "offsets": offsets,
          "average_offset_s": average, "corrections": corrections,
          "included": list(included), "final": final, "errors_ms": errors}), flush=True)


if __name__ == "__main__":
    main()
