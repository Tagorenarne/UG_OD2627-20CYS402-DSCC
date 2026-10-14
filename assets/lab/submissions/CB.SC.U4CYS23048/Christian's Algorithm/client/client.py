import socket
import time
from datetime import datetime
import json
import os

server_host = os.environ.get("SERVER_HOST", "time-server")
server_port = int(os.environ.get("SERVER_PORT", 8888))

drift = float(os.environ.get("SIMULATED_DRIFT", "12.345678"))
rounds = int(os.environ.get("ROUNDS", "5"))
interval = float(os.environ.get("INTERVAL", "3.0"))


def get_time():
    return time.time() + drift


def display_time(value):
    return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S.%f")

print("Cristian's Clock Synchronization")
print("Server :", server_host, server_port)
print("Initial Drift :", drift, "seconds")
print("Rounds :", rounds)



connected = False

for attempt in range(15):
    try:
        s = socket.socket()
        s.connect((server_host, server_port))
        s.close()

        connected = True
        print("Connected to time server")
        print()
        break

    except:
        print("Waiting for time server...")
        time.sleep(1.5)

if not connected:
    print("Could not connect to time server")
    exit()


for i in range(rounds):

    print("Round", i + 1, "/", rounds)

    try:
        s = socket.socket()
        s.connect((server_host, server_port))


        t0 = get_time()

        s.send(b"TIME_REQ")

        data = s.recv(1024)


        t1 = get_time()

        s.close()

        result = json.loads(data.decode())

        server_time = result["server_time"]
        server_time_text = result["server_time_str"]


        rtt = t1 - t0


        delay = rtt / 2


        corrected_time = server_time + delay


        correction = corrected_time - t1

        print(
            "T0              :",
            display_time(t0),
            "(", round(t0, 6), ")"
        )

        print(
            "Server Time     :",
            server_time_text,
            "(", round(server_time, 6), ")"
        )

        print(
            "T1              :",
            display_time(t1),
            "(", round(t1, 6), ")"
        )

        print("RTT             :", round(rtt * 1000, 3), "ms")
        print("Estimated Delay :", round(delay * 1000, 3), "ms")
        print("Clock Offset    :", round(correction, 6), "seconds")

        print("Before Sync     :", display_time(t1))
        print("After Sync      :", display_time(corrected_time))


        drift = drift + correction

        print("Correction      :", round(correction, 6), "seconds")
        print("Current Clock   :", display_time(get_time()))

        print("-" * 50)
        print()

    except Exception as error:
        print("Synchronization error:", error)
        print()

    if i < rounds:
        time.sleep(interval)


