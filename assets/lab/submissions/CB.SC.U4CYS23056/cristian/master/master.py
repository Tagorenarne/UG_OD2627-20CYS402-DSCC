import os
import socket
import time

HOST = "0.0.0.0"
PORT = 5000
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
DELAY_MS = int(os.getenv("DELAY_MS", "0"))
EXPECTED_CLIENTS = int(os.getenv("EXPECTED_CLIENTS", "4"))


def get_logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp)) + f".{int((timestamp % 1) * 1000):03d}"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

print("========================================", flush=True)
print("       CRISTIAN CLOCK TIME SERVER", flush=True)
print("========================================", flush=True)
print(f"Server listening on port {PORT}", flush=True)
print(f"Server clock offset : {CLOCK_OFFSET:+.3f} sec", flush=True)
print(f"Configured response delay: {DELAY_MS} ms", flush=True)
print(f"Waiting for {EXPECTED_CLIENTS} clients...\n", flush=True)

for _ in range(EXPECTED_CLIENTS):
    connection, address = server.accept()
    with connection:
        request = connection.recv(1024).decode().strip()
        parts = request.split("|")
        if len(parts) != 2 or parts[0] != "TIME_REQUEST":
            print(f"Ignored invalid request from {address}: {request}", flush=True)
            continue

        client_id = parts[1]
        # Take the server timestamp before the configurable response delay.
        server_time = get_logical_time()
        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000.0)
        connection.sendall(f"TIME|{client_id}|{server_time}".encode())

        result = connection.recv(2048).decode().strip()
        result_parts = result.split("|")
        if len(result_parts) == 6 and result_parts[0] == "RESULT":
            _, result_id, initial_clock, estimated_clock, rtt, final_clock = result_parts
            current_server_time = get_logical_time()
            error = float(final_clock) - current_server_time
            print(f"\nClient: {result_id}", flush=True)
            print(f"  Server time sent       : {format_time(server_time)}", flush=True)
            print(f"  Client initial clock   : {format_time(float(initial_clock))}", flush=True)
            print(f"  Measured RTT           : {float(rtt) * 1000:.2f} ms", flush=True)
            print(f"  Estimated one-way delay: {float(rtt) * 500:.2f} ms", flush=True)
            print(f"  Client synchronized at : {format_time(float(estimated_clock))}", flush=True)
            print(f"  Approx. error at report: {error:+.3f} sec", flush=True)
        else:
            print(f"Received invalid result from {client_id}: {result}", flush=True)

print("\n========================================", flush=True)
print("       CRISTIAN SYNCHRONIZATION DONE", flush=True)
print("========================================", flush=True)
server.close()
