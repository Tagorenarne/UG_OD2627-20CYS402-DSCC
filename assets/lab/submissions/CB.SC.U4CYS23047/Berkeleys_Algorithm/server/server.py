import socket
import time
import os

HOST = "0.0.0.0"
PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + CLOCK_OFFSET


def main():

    # Create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen()

    print("[SERVER] Berkeley Server started")
    print(f"[SERVER] Listening on port {PORT}")

    clients = []

    # Wait for 4 clients
    for i in range(4):

        conn, address = server.accept()

        print(
            f"[SERVER] Client {i + 1} connected: "
            f"{address}"
        )

        data = conn.recv(1024).decode().strip()

        if data:
            client_time = float(data)

            clients.append(
                (conn, address, client_time)
            )

            print(
                f"[SERVER] Received time from {address}: "
                f"{client_time:.3f}"
            )

    print("\n[SERVER] All 4 clients connected.")

    server_time = get_time()

    print(
        f"[SERVER] Current time: "
        f"{server_time:.3f}"
    )

    all_times = [server_time]

    for _, address, client_time in clients:

        print(
            f"[SERVER] {address} -> "
            f"{client_time:.3f}"
        )

        all_times.append(client_time)

    # Calculate average time
    tx = sum(all_times) / len(all_times)

    print("\n[SERVER] Calculated average Tx:")
    print(f"[SERVER] Tx = {tx:.3f}")

    server_delay = tx - server_time

    print(
        f"[SERVER] Server correction = "
        f"{server_delay:+.3f} seconds"
    )

    # Send correction to each client
    for conn, address, client_time in clients:

        delay = tx - client_time

        print(
            f"[SERVER] Sending correction to {address}: "
            f"{delay:+.3f} seconds"
        )

        conn.sendall(
            f"{delay:.3f}".encode()
        )

        conn.close()

    print("\n[SERVER] Synchronization complete.")

    print(
        f"[SERVER] New server time: "
        f"{server_time + server_delay:.3f}"
    )

    server.close()


if __name__ == "__main__":
    main()