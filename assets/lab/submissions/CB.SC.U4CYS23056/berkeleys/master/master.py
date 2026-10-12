import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

CLIENTS = [
    "clock-client1",
    "clock-client2",
    "clock-client3",
    "clock-client4"
]


def get_logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime(
        "%H:%M:%S",
        time.localtime(timestamp)
    ) + f".{int((timestamp % 1) * 1000):03d}"




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

print("========================================")
print("       BERKELEY CLOCK MASTER")
print("========================================")
print(f"Master started on port {PORT}")
print(f"Master Clock Offset : {CLOCK_OFFSET} seconds")
print("Waiting for clients...\n")




client_times = {}
client_connections = {}



for client_number in range(1, 5):

    connection, address = server.accept()

    # Send CLOCK_REQUEST
    connection.send("CLOCK_REQUEST".encode())

    # Receive client clock
    response = connection.recv(1024).decode()

    parts = response.split("|")

    if len(parts) == 3 and parts[0] == "CLOCK":

        client_id = parts[1]
        client_time = float(parts[2])

        client_times[client_id] = client_time
        client_connections[client_id] = connection

        print(
            f"Received from {client_id}: "
            f"{format_time(client_time)}"
        )




master_time = get_logical_time()




print()
print("========== BERKELEY ALGORITHM ==========")

print()
print("Initial Clocks")
print()

print(f"Master       : {format_time(master_time)}")

for client_id in sorted(client_times):
    print(
        f"{client_id.replace('clock-', '').title():<13}: "
        f"{format_time(client_times[client_id])}"
    )




master_offset = 0.0

offsets = {}

for client_id, client_time in client_times.items():

    offset = client_time - master_time

    offsets[client_id] = offset


print()
print("------------------------------------------")
print()
print("Clock Offsets")
print()

print(f"Master       : {master_offset:+.3f} sec")

for client_id in sorted(offsets):

    display_name = client_id.replace(
        "clock-", ""
    ).title()

    print(
        f"{display_name:<13}: "
        f"{offsets[client_id]:+.3f} sec"
    )




all_offsets = [master_offset]

for offset in offsets.values():
    all_offsets.append(offset)


average_offset = sum(all_offsets) / len(all_offsets)


print()
print(f"Average Offset: {average_offset:+.3f} sec")




master_correction = average_offset - master_offset

corrections = {}

for client_id, offset in offsets.items():

    correction = average_offset - offset

    corrections[client_id] = correction


print()
print("------------------------------------------")
print()
print("Corrections")
print()

print(
    f"Master       : "
    f"{master_correction:+.3f} sec"
)

for client_id in sorted(corrections):

    display_name = client_id.replace(
        "clock-", ""
    ).title()

    print(
        f"{display_name:<13}: "
        f"{corrections[client_id]:+.3f} sec"
    )




for client_id, connection in client_connections.items():

    correction = corrections[client_id]

    message = f"CORRECTION|{correction}"

    connection.send(message.encode())



final_master_time = master_time + master_correction




final_client_times = {}

for client_id, connection in client_connections.items():

    response = connection.recv(1024).decode()

    parts = response.split("|")

    if len(parts) == 3 and parts[0] == "FINAL":

        final_time = float(parts[2])

        final_client_times[client_id] = final_time

    connection.close()




print()
print("------------------------------------------")
print()
print("Final Clocks")
print()

print(
    f"Master       : "
    f"{format_time(final_master_time)}"
)

for client_id in sorted(final_client_times):

    display_name = client_id.replace(
        "clock-", ""
    ).title()

    print(
        f"{display_name:<13}: "
        f"{format_time(final_client_times[client_id])}"
    )


print()
print("==========================================")
print("       SYNCHRONIZATION COMPLETE")
print("==========================================")
print()


server.close()