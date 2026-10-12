"""Berkeley algorithm - master / coordinator.
Env: CLIENTS="host:port,..."  MASTER_OFFSET  OUTLIER_THRESHOLD (0=off)  EXPERIMENT_ID  TIMEOUT"""
import json, os, socket, time

CLIENTS = [c.strip() for c in os.getenv("CLIENTS", "clock-client1:5000,clock-client2:5000,clock-client3:5000,clock-client4:5000").split(",")]
MASTER_OFFSET = float(os.getenv("MASTER_OFFSET", "0"))
THRESHOLD = float(os.getenv("OUTLIER_THRESHOLD", "0"))   # ENHANCEMENT, not part of basic Berkeley
EXPERIMENT = os.getenv("EXPERIMENT_ID", "1")
TIMEOUT = float(os.getenv("TIMEOUT", "3"))


def fmt(ts):
    return time.strftime("%H:%M:%S", time.gmtime(ts)) + f"{ts % 1:.3f}"[1:]


class Clock:
    def __init__(self, offset): self.offset = offset
    def now(self): return time.time() + self.offset


master_clock = Clock(MASTER_OFFSET)


def rpc(addr, msg, retries=1):
    """Send one message; return (reply, master time at RTT midpoint, RTT) or None."""
    host, port = addr.split(":")
    for _ in range(retries):
        try:
            with socket.create_connection((host, int(port)), timeout=TIMEOUT) as s:
                f = s.makefile("rw")
                t0 = master_clock.now()
                f.write(json.dumps(msg) + "\n"); f.flush()
                reply = json.loads(f.readline())
                t1 = master_clock.now()
                return reply, (t0 + t1) / 2, t1 - t0
        except (OSError, ValueError):
            time.sleep(1)
    return None


def poll(retries=1):
    """CLOCK_REQUEST to every client. offset = client clock - master clock at RTT midpoint."""
    res = {}
    for c in CLIENTS:
        r = rpc(c, {"type": "CLOCK_REQUEST"}, retries)
        if r is None:
            res[c] = None
        else:
            reply, mid, rtt = r
            res[c] = {"clock": reply["clock"], "offset": reply["clock"] - mid, "rtt": rtt}
    return res


def main():
    names = ["Master"] + [f"Client {i+1}" for i in range(len(CLIENTS))]
    print("========== BERKELEY ALGORITHM ==========")
    print(f"Experiment {EXPERIMENT} | outlier threshold: {THRESHOLD if THRESHOLD else 'OFF (basic Berkeley)'}\n")

    polled = poll(retries=15)          # retries let clients finish booting
    nodes = {"Master": {"clock": master_clock.now(), "offset": 0.0, "alive": True, "used": True, "addr": None}}
    for name, c in zip(names[1:], CLIENTS):
        p = polled[c]
        nodes[name] = ({"clock": p["clock"], "offset": p["offset"], "alive": True, "used": True, "addr": c}
                       if p else {"clock": None, "offset": None, "alive": False, "used": False, "addr": c})

    print("Initial Clocks\n")
    for n, d in nodes.items():
        print(f"{n:<10}: {fmt(d['clock']) if d['alive'] else 'NO RESPONSE'}")
    print("\n" + "-" * 42 + "\n\nClock Offsets\n")
    for n, d in nodes.items():
        print(f"{n:<10}: {d['offset']:+.3f} sec" if d["alive"] else f"{n:<10}: unreachable")

    if THRESHOLD:   # optional enhancement: outlier exclusion
        for n, d in nodes.items():
            if d["alive"] and n != "Master" and abs(d["offset"]) > THRESHOLD:
                d["used"] = False
                print(f"  ** {n} EXCLUDED from average (|offset| {abs(d['offset']):.1f} > {THRESHOLD}) [enhancement]")

    used = [d["offset"] for d in nodes.values() if d["used"]]
    avg = sum(used) / len(used)
    print(f"\nAverage Offset: {avg:+.3f} sec   (over {len(used)} nodes)")

    print("\n" + "-" * 42 + "\n\nCorrections\n")   # excluded-but-alive nodes are still corrected
    for n, d in nodes.items():
        if d["alive"]:
            d["corr"] = avg - d["offset"]
            print(f"{n:<10}: {d['corr']:+.3f} sec")
    for d in nodes.values():
        if d["alive"] and d["addr"]:
            rpc(d["addr"], {"type": "CORRECTION", "value": d["corr"]})
    master_clock.offset += nodes["Master"]["corr"]

    final = poll()
    print("\n" + "-" * 42 + "\n\nFinal Clocks\n")
    nodes["Master"]["final"], nodes["Master"]["ferr"] = master_clock.now(), 0.0
    for n, d in nodes.items():
        if n != "Master":
            p = final.get(d["addr"])
            d["final"], d["ferr"] = (p["clock"], p["offset"]) if p else (None, None)
    for n, d in nodes.items():
        print(f"{n:<10}: {fmt(d['final']) if d['final'] else 'NO RESPONSE'}" +
              (f"   (error vs master {d['ferr']*1000:+.1f} ms)" if d["final"] else ""))
    errs = [abs(d["ferr"]) for d in nodes.values() if d["final"]]
    print(f"\nFinal synchronization error (max deviation from master): {max(errs)*1000:.1f} ms")

    print("\n| Exp | Node | Initial Clock | Offset (s) | Avg Offset (s) | Correction (s) | Final Clock | Error (ms) |")
    print("|---|---|---|---:|---:|---:|---|---:|")
    for n, d in nodes.items():
        if not d["alive"]:
            print(f"| {EXPERIMENT} | {n} | NO RESPONSE | - | - | - | - | - |")
        elif d["final"]:
            print(f"| {EXPERIMENT} | {n} | {fmt(d['clock'])} | {d['offset']:+.3f} | {avg:+.3f} | {d['corr']:+.3f} | {fmt(d['final'])} | {d['ferr']*1000:+.1f} |")
        else:
            print(f"| {EXPERIMENT} | {n} | {fmt(d['clock'])} | {d['offset']:+.3f} | {avg:+.3f} | {d['corr']:+.3f} | - | - |")


if __name__ == "__main__":
    main()
