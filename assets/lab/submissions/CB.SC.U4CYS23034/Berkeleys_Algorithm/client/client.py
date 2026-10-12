import os
import socket
import time


def main():
    name = os.getenv("CLIENT_ID", "Client")
    offset = float(os.getenv("CLOCK_OFFSET", "0"))
    host = os.getenv("SERVER_HOST", "server")

    for attempt in range(30):
        try:
            client = socket.create_connection((host, 5000), timeout=30)
            break
        except OSError:
            time.sleep(0.2)
    else:
        raise ConnectionError("Could not connect to the coordinator")

    with client, client.makefile("r") as stream:
        client.sendall(f"{name}\n".encode())
        if stream.readline().strip() != "TIME":
            raise ValueError("Expected a clock request")
        before = time.time() + offset
        client.sendall(f"{before:.9f}\n".encode())
        correction = float(stream.readline())
        offset += correction
        after = time.time() + offset
        client.sendall(f"{after:.9f}\n".encode())

    print(f"\n{name} - Berkeley's algorithm")
    print(f"Clock before : {before:.3f}")
    print(f"Correction   : {correction:+.6f} seconds")
    print(f"Clock after  : {after:.3f}")


if __name__ == "__main__":
    main()
