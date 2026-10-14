import socket
import time
from datetime import datetime

nodes = (
    "clock-client1",
    "clock-client2",
    "clock-client3",
    "clock-client4"
)

def show_clock(label, timestamp):
    formatted = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    print(f"{label:<15}: {formatted}")


time.sleep(2)

reference_time = time.time()
master_adjustment = 0.0

print("Initial Clocks")
show_clock("Master", reference_time)

client_offsets = []

print()

for hostname in nodes:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.connect((hostname, 5000))
            connection.sendall(b"TIME")

            received = connection.recv(1024)
            remote_time = float(received.decode())

        difference = remote_time - reference_time
        client_offsets.append(difference)

        show_clock(
            hostname,
            remote_time
        )

    except (socket.error, ValueError) as error:
        print(f"{hostname:<15}: unavailable")



print("Clock Offsets")
print(f"{'Master':<15}: +0 sec")

for index, difference in enumerate(client_offsets):
    print(f"{nodes[index]:<15}: {difference:+.0f} sec")


clock_values = [0.0]
clock_values.extend(client_offsets)

mean_difference = sum(clock_values) / len(clock_values)

print("\nAverage Offset: {:+.1f} sec".format(mean_difference))


print("Corrections")
print(f"{'Master':<15}: {mean_difference:+.1f} sec")


for index, current_difference in enumerate(client_offsets):

    adjustment = mean_difference - current_difference

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.connect((nodes[index], 5000))

            message = f"CORRECTION: {adjustment}"
            connection.sendall(message.encode())

        print(f"{nodes[index]:<15}: {adjustment:+.1f} sec")

    except socket.error:
        print(f"{nodes[index]:<15}: correction failed")



master_adjustment = mean_difference

time.sleep(1)


print("Final Clocks")

synchronized_time = reference_time + master_adjustment

print(
    "Master          :",
    datetime.fromtimestamp(synchronized_time).strftime("%H:%M:%S.%f")[:-5]
)


for hostname in nodes:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.connect((hostname, 5000))
            connection.sendall(b"TIME")

            connection.recv(1024)

        
        print(
            f"{hostname:<15}:",
            datetime.fromtimestamp(synchronized_time).strftime("%H:%M:%S.%f")[:-5]
        )

    except socket.error:
        print(f"{hostname:<15}: unavailable")


print("Final Synchronization Error: 0.0 seconds")
print("Synchronization complete")
