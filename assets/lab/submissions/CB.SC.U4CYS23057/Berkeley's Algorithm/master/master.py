import os
import time
import urllib.request

master_offset = float(os.getenv("CLOCK_OFFSET", "0"))
threshold = float(os.getenv("THRESHOLD", "0"))  
clients = os.getenv("CLIENTS", "").split(",")


def master_clock():
    return time.time() + master_offset


def fmt(t):
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int(t % 1 * 1000):03d}"


def poll(addr):
    start = master_clock()
    with urllib.request.urlopen(f"http://{addr}/time", timeout=2) as r:
        t = float(r.read())
    rtt = master_clock() - start
    return t + rtt / 2


def send_correction(addr, c):
    urllib.request.urlopen(f"http://{addr}/adjust?correction={c}", timeout=2).read()


time.sleep(3)  # give clients time to start

nodes = [{"name": "Master", "addr": None, "clock": master_clock(), "offset": 0.0}]
for i, addr in enumerate(clients, 1):
    name = f"Client {i}"
    try:
        t = poll(addr)
    except Exception:
        print(f"{name:<12} : NO RESPONSE (skipped)")
        continue
    nodes.append({"name": name, "addr": addr, "clock": t, "offset": t - master_clock()})

print("\nBERKELEY ALGORITHM")
print("\nInitial Clocks\n")
for n in nodes:
    print(f"{n['name']:<12} : {fmt(n['clock'])}")

print("\n------------------------------------------\nClock Offsets\n")
for n in nodes:
    n["excluded"] = threshold > 0 and abs(n["offset"]) > threshold
    note = "  <- outlier, excluded from average" if n["excluded"] else ""
    print(f"{n['name']:<12} : {n['offset']:+.2f} sec{note}")

used = [n["offset"] for n in nodes if not n["excluded"]]
avg = sum(used) / len(used)
print(f"\nAverage Offset: {avg:+.2f} sec (over {len(used)} nodes)")

print("\n------------------------------------------\nCorrections\n")
for n in nodes:
    c = avg - n["offset"]
    print(f"{n['name']:<12} : {c:+.2f} sec")
    if n["addr"] is None:
        master_offset += c  # master corrects itself
    else:
        send_correction(n["addr"], c)

print("\n------------------------------------------\nFinal Clocks\n")
diffs = []
for n in nodes:
    t = master_clock() if n["addr"] is None else poll(n["addr"])
    diffs.append(t - master_clock())
    print(f"{n['name']:<12} : {fmt(t)}")

print(f"\nFinal synchronization error (max - min): {max(diffs) - min(diffs):.3f} sec")
