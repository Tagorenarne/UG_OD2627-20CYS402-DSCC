
import json
import os
import socket
import time
from datetime import datetime, timezone

MASTER_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))
CLIENTS_ENV = os.environ.get("CLIENTS", "") 
POLL_DELAY = float(os.environ.get("POLL_DELAY", "3"))
OUTLIER_FILTER = os.environ.get("OUTLIER_FILTER", "false").lower() == "true"
OUTLIER_THRESHOLD = float(os.environ.get("OUTLIER_THRESHOLD", "15"))


def parse_clients(env: str):
    clients = []
    for entry in env.split(","):
        entry = entry.strip()
        if not entry:
            continue
        host, port = entry.split(":")
        clients.append((host, int(port)))
    return clients


def send_recv(host, port, message, timeout=5):
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.sendall((json.dumps(message) + "\n").encode())
        f = s.makefile("r")
        return json.loads(f.readline())


def fmt(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]


def line():
    print("-" * 44, flush=True)


def main():
    global MASTER_OFFSET
    master_offset = MASTER_OFFSET
    clients = parse_clients(CLIENTS_ENV)

    print("========== BERKELEY ALGORITHM ==========\n", flush=True)
    print(f"Waiting {POLL_DELAY:.0f}s for client containers to come up...\n", flush=True)
    time.sleep(POLL_DELAY)

    def master_clock():
        return time.time() + master_offset

    # initial clocks
    print("Initial Clocks\n", flush=True)
    master_initial = master_clock()
    print(f"Master       : {fmt(master_initial)}", flush=True)

    nodes = {}  
    for host, port in clients:
        try:
            resp = send_recv(host, port, {"cmd": "CLOCK_REQUEST"})
            cid = resp.get("client_id", host)
            nodes[cid] = {"host": host, "port": port, "time": resp["time"]}
            print(f"{cid:<13}: {fmt(resp['time'])}", flush=True)
        except Exception as e:
            print(f"{host:<13}: UNREACHABLE ({e})", flush=True)

    print()
    line()
    print()

    # offsets relative to master 
    print("Clock Offsets\n", flush=True)
    offsets = {"Master": 0.0}
    print(f"Master       : {0:+.2f} sec", flush=True)
    for cid, data in nodes.items():
        off = data["time"] - master_initial
        offsets[cid] = off
        print(f"{cid:<13}: {off:+.2f} sec", flush=True)

    
    included = dict(offsets)
    excluded = {}
    if OUTLIER_FILTER:
        for cid, off in list(included.items()):
            if cid != "Master" and abs(off) > OUTLIER_THRESHOLD:
                excluded[cid] = included.pop(cid)
        if excluded:
            print(
                f"\n[Outlier filter ENABLED] Excluding nodes beyond "
                f"+/-{OUTLIER_THRESHOLD:.0f}s: {list(excluded.keys())}",
                flush=True,
            )
               

    avg_offset = sum(included.values()) / len(included)
    print(f"\nAverage Offset: {avg_offset:+.2f} sec", flush=True)

    print()
    line()
    print()

    # corrections
    print("Corrections\n", flush=True)
    corrections = {}
    master_correction = avg_offset - offsets["Master"]
    corrections["Master"] = master_correction
    print(f"Master       : {master_correction:+.2f} sec", flush=True)

    for cid, off in offsets.items():
        if cid == "Master":
            continue
        if cid in excluded:
            print(f"{cid:<13}: EXCLUDED (no correction sent)", flush=True)
            continue
        corr = avg_offset - off
        corrections[cid] = corr
        print(f"{cid:<13}: {corr:+.2f} sec", flush=True)

    print()
    line()
    print()

    # apply corrections
    master_offset += master_correction
    for cid, data in nodes.items():
        if cid in excluded:
            continue
        try:
            send_recv(data["host"], data["port"], {"cmd": "CORRECTION", "value": corrections[cid]})
        except Exception as e:
            print(f"Failed to send correction to {cid}: {e}", flush=True)

 
    print("Final Clocks\n", flush=True)
    final = {"Master": master_clock()}# after applying correction, the master's new logical clock
    print(f"Master       : {fmt(final['Master'])}", flush=True)

    for cid, data in nodes.items():
        try:
            resp = send_recv(data["host"], data["port"], {"cmd": "CLOCK_REQUEST"})
            final[cid] = resp["time"]
            print(f"{cid:<13}: {fmt(resp['time'])}", flush=True)
        except Exception as e:
            print(f"{cid:<13}: UNREACHABLE ({e})", flush=True)

    print()
    line()
    print()

    spread_ms = (max(final.values()) - min(final.values())) * 1000
    print(f"Final synchronization error (max-min spread): {spread_ms:.1f} ms", flush=True)


if __name__ == "__main__":
    main()
