import os
import socket
import time


def main():
    offset = float(os.getenv("CLOCK_OFFSET", "0"))
    clients = []

    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 5000))
        server.listen()
        server.settimeout(30)
        print("Waiting for four clients...", flush=True)

        try:
            for _ in range(4):
                connection, address = server.accept()
                connection.settimeout(30)
                stream = connection.makefile("r")
                name = stream.readline().strip()
                if not name:
                    stream.close()
                    connection.close()
                    raise ValueError("Client did not send its name")
                clients.append((connection, stream, name))
                print(f"{name} connected", flush=True)

            readings = []
            for connection, stream, name in clients:
                start = time.time() + offset
                connection.sendall(b"TIME\n")
                client_time = float(stream.readline())
                end = time.time() + offset
                difference = client_time - (start + end) / 2
                readings.append((connection, stream, name, client_time, difference))

            average = sum(row[4] for row in readings) / (len(readings) + 1)
            print(f"\nAverage offset: {average:+.6f} seconds")
            print(f"Server correction: {average:+.6f} seconds")
            offset += average

            for connection, stream, name, before, difference in readings:
                correction = average - difference
                connection.sendall(f"{correction:.9f}\n".encode())
                start = time.time() + offset
                after = float(stream.readline())
                end = time.time() + offset
                error = abs(after - (start + end) / 2)
                print(f"{name}: before={before:.3f}, offset={difference:+.3f}s, "
                      f"correction={correction:+.3f}s, after={after:.3f}, error={error * 1000:.3f}ms")

            print(f"Server clock after correction: {time.time() + offset:.3f}")
        finally:
            for connection, stream, name in clients:
                stream.close()
                connection.close()


if __name__ == "__main__":
    main()
