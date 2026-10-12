import socket
import datetime
import os
import time

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
DELAY_MS = float(os.getenv("DELAY_MS", "0"))


def get_logical_time():
    return datetime.datetime.now() + datetime.timedelta(seconds=CLOCK_OFFSET)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print("========================================")
    print("      CRISTIAN CLOCK MASTER SERVER")
    print("========================================")
    print(f"Listening on port : {PORT}")
    print(f"Clock Offset      : {CLOCK_OFFSET} seconds")
    print(f"Artificial Delay  : {DELAY_MS} ms")
    print("Waiting for clients...\n")

    while True:
        connection, address = server.accept()

        try:
            request = connection.recv(1024).decode().strip()

            print(f"Request from {address}: {request}")

            if request == "TIME_REQUEST":
                master_time = get_logical_time()

                if DELAY_MS > 0:
                    time.sleep(DELAY_MS / 1000)

                response = f"MASTER_TIME = {master_time.isoformat()}"

                connection.sendall(response.encode())

                print(f"Master Time: {master_time}")
                print(f"Response sent to {address}\n")

        except Exception as e:
            print("Error:", e)

        finally:
            connection.close()


if __name__ == "__main__":
    start_server()