import socket
import time
import os
from datetime import datetime

SERVER_HOST = os.getenv("SERVER_HOST", "clock-master")
SERVER_PORT = 5050

CLIENT_ID = os.getenv("CLIENT_ID", "client1")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


print("CRISTIAN CLOCK CLIENT")

print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Offset  : {CLOCK_OFFSET} seconds")
print(f"Server          : {SERVER_HOST}:{SERVER_PORT}")


while True:

    try:

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        # T1 - client logical time before request
        T1_real = time.time()
        T1 = T1_real + CLOCK_OFFSET

        client_socket.connect(
            (SERVER_HOST, SERVER_PORT)
        )

        # Send time request
        client_socket.send(b"TIME_REQUEST")

        # Receive master time
        data = client_socket.recv(1024)

        # T2 - client logical time after response
        T2_real = time.time()
        T2 = T2_real + CLOCK_OFFSET

        master_time = float(data.decode())

        client_socket.close()

        # Cristian's Algorithm

        RTT = T2 - T1

        estimated_delay = RTT / 2

        corrected_clock = master_time + estimated_delay

        clock_correction = corrected_clock - T2

        final_error = corrected_clock - master_time

        print("\n")
        print("CRISTIAN'S ALGORITHM RESULT")

        print(f"Client ID          : {CLIENT_ID}")

        print(
            f"Initial Clock      : "
            f"{datetime.fromtimestamp(T1)}"
        )

        print(
            f"T1                 : "
            f"{datetime.fromtimestamp(T1)}"
        )

        print(
            f"Master Time        : "
            f"{datetime.fromtimestamp(master_time)}"
        )

        print(
            f"T2                 : "
            f"{datetime.fromtimestamp(T2)}"
        )

        print(f"RTT                : {RTT:.6f} seconds")

        print(
            f"Estimated Delay    : "
            f"{estimated_delay:.6f} seconds"
        )

        print(
            f"Corrected Clock    : "
            f"{datetime.fromtimestamp(corrected_clock)}"
        )

        print(
            f"Clock Correction   : "
            f"{clock_correction:.6f} seconds"
        )

        print(
            f"Final Error        : "
            f"{final_error:.6f} seconds"
        )



        # Wait before next synchronization
        time.sleep(5)

    except ConnectionRefusedError:

        print("Master not ready. Retrying in 1 second...")
        time.sleep(1)

    except Exception as e:

        print("Client error:", e)
        time.sleep(1)
