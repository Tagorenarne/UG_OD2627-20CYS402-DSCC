import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

# Configurable logical clock offset
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

# Artificial processing delay in seconds
ARTIFICIAL_DELAY = float(os.getenv("ARTIFICIAL_DELAY", "0"))


def logical_time():
    """
    Return the master's logical time.
    """
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    """
    Convert timestamp into HH:MM:SS.mmm format.
    """
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


# Create TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow socket reuse
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind server
server.bind((HOST, PORT))

# Start listening
server.listen()

print("=" * 50, flush=True)
print("      CRISTIAN'S TIME SERVER", flush=True)
print("=" * 50, flush=True)
print(f"Server Host       : {HOST}", flush=True)
print(f"Server Port       : {PORT}", flush=True)
print(f"Clock Offset      : {CLOCK_OFFSET} seconds", flush=True)
print(f"Artificial Delay  : {ARTIFICIAL_DELAY} seconds", flush=True)
print("Server Status     : RUNNING", flush=True)
print("=" * 50, flush=True)


while True:

    # Wait for a client connection
    connection, address = server.accept()

    with connection:

        # Receive request
        request = connection.recv(1024).decode().strip()

        if request == "TIME_REQUEST":

            print("\n----------------------------------------", flush=True)
            print(
                f"TIME_REQUEST received from {address}",
                flush=True
            )

            # Introduce optional artificial delay
            if ARTIFICIAL_DELAY > 0:
                print(
                    f"Applying artificial delay: "
                    f"{ARTIFICIAL_DELAY} seconds",
                    flush=True
                )

                time.sleep(ARTIFICIAL_DELAY)

            # Get master's logical time
            master_timestamp = logical_time()

            master_formatted = format_time(master_timestamp)

            # Send timestamp to client
            response = str(master_timestamp)
            connection.sendall(response.encode())

            print(
                f"Master Time Sent : {master_formatted}",
                flush=True
            )
            print("----------------------------------------", flush=True)

        else:

            print(
                f"Unknown request from {address}: {request}",
                flush=True
            )