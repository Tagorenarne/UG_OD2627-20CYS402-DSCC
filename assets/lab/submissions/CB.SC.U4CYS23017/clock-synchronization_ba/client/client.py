import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5001

CLIENT_ID = os.environ.get("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]


print("=" * 45)
print(f"        {CLIENT_ID.upper()}")
print("=" * 45)

print(f"Initial Clock Offset : {CLOCK_OFFSET:+.2f} seconds")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))

server.listen(5)

print(f"Listening on port {PORT}...")
print("Waiting for master requests...\n")


while True:

    conn, addr = server.accept()

    try:

        data = conn.recv(1024).decode().strip()

        if data == "CLOCK_REQUEST":

            current_clock = logical_time()

            print("---------------------------------------------")
            print("CLOCK REQUEST RECEIVED")
            print(f"Client ID : {CLIENT_ID}")
            print(f"Current Clock : {format_time(current_clock)}")

            response = f"CLOCK:{current_clock}\n"

            conn.sendall(response.encode())

            # Wait for correction
            conn.settimeout(5)

            try:

                correction_data = conn.recv(1024).decode().strip()

                if correction_data.startswith("CORRECTION:"):

                    correction = float(
                        correction_data.split(":")[1]
                    )

                    old_clock = logical_time()

                    CLOCK_OFFSET += correction

                    new_clock = logical_time()

                    print(f"Correction Received : {correction:+.2f} seconds")
                    print(f"Clock Before        : {format_time(old_clock)}")
                    print(f"Clock After         : {format_time(new_clock)}")

            except socket.timeout:

                pass

        conn.close()

    except Exception as e:

        print("Error:", e)

        try:
            conn.close()
        except:
            pass
