import socket, os, time

off = float(os.environ["CLOCK_OFFSET"])
cid = os.environ["CLIENT_ID"]
clock = lambda: time.time() + off
fmt = lambda t: time.strftime("%H:%M:%S", time.gmtime(t + 19800)) + f".{int(t % 1 * 10)}"

s = socket.create_server(("", 5000))
print(f"[{cid}] started, clock = {fmt(clock())} (offset {off:+} sec)")
while True:
    conn, _ = s.accept()
    msg = conn.recv(64).decode()
    if msg == "CLOCK_REQUEST":
        conn.sendall(str(clock()).encode())
    else:
        print(f"[{cid}] before: {fmt(clock())}")
        off += float(msg)
        print(f"[{cid}] correction {float(msg):+.1f} sec -> after: {fmt(clock())}")
    conn.close()