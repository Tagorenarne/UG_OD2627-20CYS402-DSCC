import socket
import time
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

MASTER_HOST = "clock-master"
MASTER_PORT = 5000


def get_logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime(
        "%H:%M:%S",
        time.localtime(timestamp)
    ) + f".{int((timestamp % 1) * 1000):03d}"




client = socket.socket()

client.connect(
    (MASTER_HOST, MASTER_PORT)
)




request = client.recv(1024).decode()


if request == "CLOCK_REQUEST":

    # Get current logical clock
    client_time = get_logical_time()

    # Send clock value to master
    message = f"CLOCK|{CLIENT_ID}|{client_time}"

    client.send(message.encode())




response = client.recv(1024).decode()

parts = response.split("|")


if len(parts) == 2 and parts[0] == "CORRECTION":

    correction = float(parts[1])

else:

    correction = 0.0




final_time = client_time + correction




print()
print("========================================")
print("       BERKELEY CLIENT")
print("========================================")

print(f"Client ID        : {CLIENT_ID}")
print(f"Clock Offset     : {CLOCK_OFFSET:+.3f} sec")

print("----------------------------------------")

print(
    f"Initial Clock    : "
    f"{format_time(client_time)}"
)

print(
    f"Correction       : "
    f"{correction:+.3f} sec"
)

print("----------------------------------------")

print(
    f"Final Clock      : "
    f"{format_time(final_time)}"
)

print("========================================")
print()




message = f"FINAL|{CLIENT_ID}|{final_time}"

client.send(message.encode())

client.close()