import socket, os, time

off = float(os.environ.get("CLOCK_OFFSET", 0))
clients = os.environ["CLIENTS"].split(",")
MAX_SKEW = float(os.environ.get("MAX_SKEW", 30))
clock = lambda: time.time() + off
fmt = lambda t: time.strftime("%H:%M:%S", time.gmtime(t + 19800)) + f".{int(t % 1 * 10)}"

def ask(host, msg):
    with socket.create_connection((host, 5000), timeout=2) as s:
        s.sendall(msg.encode())
        return s.recv(64).decode()

def poll():
    t = {"master": clock()}
    for c in clients:
        try: t[c] = float(ask(c, "CLOCK_REQUEST"))
        except OSError: print(f"{c}: no response, skipped")
    return t

time.sleep(2)
print("========== BERKELEY ALGORITHM ==========\n\nInitial Clocks")
t = poll()
for n, v in t.items(): print(f"{n:12}: {fmt(v)}")

offs = {n: v - t["master"] for n, v in t.items()}
print("\nClock Offsets")
for n, o in offs.items(): print(f"{n:12}: {o:+.1f} sec" + ("  (FAULTY - ignored in average)" if abs(o) > MAX_SKEW else ""))

good = [o for o in offs.values() if abs(o) <= MAX_SKEW]
avg = sum(good) / len(good)
print(f"\nAverage Offset: {avg:+.1f} sec\n\nCorrections")
for n, o in offs.items():
    print(f"{n:12}: {avg - o:+.1f} sec")
    if n == "master": off += avg - o
    else: ask(n, str(avg - o))

print("\nFinal Clocks")
for n, v in poll().items(): print(f"{n:12}: {fmt(v)}")