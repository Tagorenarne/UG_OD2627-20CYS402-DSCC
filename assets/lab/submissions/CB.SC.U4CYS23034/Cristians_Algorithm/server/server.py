import os
import socket
import time


def main():
    offset = float(os.getenv("CLOCK_OFFSET", "0"))
    delay = float(os.getenv("RESPONSE_DELAY", "0"))

    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 5000))
        server.listen()
        print("Time server running on port 5000", flush=True)

        while True:
            connection, address = server.accept()
            with connection:
                connection.settimeout(15)
                with connection.makefile("r") as stream:
                    if stream.readline().strip() != "TIME":
                        continue
                time.sleep(delay)
                current = time.time() + offset
                connection.sendall(f"{current:.9f} {offset}\n".encode())
                print(f"Sent time to {address[0]}: {current:.3f}", flush=True)


if __name__ == "__main__":
    main()
