import socket
import time
import os

from datetime import datetime


SERVER_HOST = "clock-master"
SERVER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "Client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

initial_clock = logical_time()

T1 = logical_time()
#time at which the req is sent

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_HOST, SERVER_PORT))

# Receives time from server as data
data = client.recv(1024)

#time at which client receives the response
T2 = logical_time()

client.close()


#The time that server has sent
Ts = float(data.decode())


#christian's algo
RTT = T2 - T1
delay = RTT / 2
Tc = Ts + delay


initial_datetime = format_time(initial_clock)
T1_datetime = format_time(T1)
Ts_datetime = format_time(Ts)
T2_datetime = format_time(T2)
Tc_datetime = format_time(Tc)

actual_time = time.time()
error = abs(Tc - actual_time)


print()
print("CHRISTIAN'S ALGORITHM ==========>")
print()
print(f"Client ID       : {CLIENT_ID}")
print(f"Clock Offset    : {CLOCK_OFFSET:+.2f} seconds")
print()
print(f"Initial Clock   : {initial_datetime}")
print()
print(f"T1              : {T1_datetime}")
print(f"Server Time     : {Ts_datetime}")
print(f"T2              : {T2_datetime}")
print()
print(f"RTT             : {RTT * 1000:.3f} ms")
print(f"Estimated Delay : {delay * 1000:.3f} ms")
print()
print(f"Corrected Clock : {Tc_datetime}")
print(f"Final Error     : {error * 1000:.3f} ms")
print()

