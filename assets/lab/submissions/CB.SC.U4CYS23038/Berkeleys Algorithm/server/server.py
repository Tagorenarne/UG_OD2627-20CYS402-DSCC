import socket
import time
import os

server_host = "0.0.0.0"
server_port = 5000

clock_offset = float(os.getenv("CLOCK_OFFSET", "0"))

def get_current_time():
    return time.time() + clock_offset

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )
    server_socket.bind((server_host, server_port))
    server_socket.listen()
    print("[SERVER] Berkeley Server started")
    print(f"[SERVER] Listening on port {server_port}")

    connected_clients = []

    for client_number in range(4):

        client_connection, client_address = server_socket.accept()

        print(
            f"[SERVER] Client {client_number + 1} connected: "
            f"{client_address}"
        )

        received_data = client_connection.recv(1024).decode().strip()

        if received_data:
            client_time = float(received_data)

            connected_clients.append(
                (client_connection, client_address, client_time)
            )

            print(
                f"[SERVER] Received time from {client_address}: "
                f"{client_time:.3f}"
            )

    print("\n[SERVER] All 4 clients connected.")

    server_time = get_current_time()

    print(f"[SERVER] Current time: {server_time:.3f}")

    all_client_times = [server_time]

    for connection, address, client_time in connected_clients:

        print(f"[SERVER] {address} -> {client_time:.3f}")

        all_client_times.append(client_time)

    average_time = sum(all_client_times) / len(all_client_times)

    print("\n[SERVER] Calculated average time:")
    print(f"[SERVER] Average = {average_time:.3f}")

    server_correction = average_time - server_time

    print(
        f"[SERVER] Server correction = "
        f"{server_correction:+.3f} seconds"
    )

    for client_connection, client_address, client_time in connected_clients:

        time_correction = average_time - client_time

        print(
            f"[SERVER] Sending correction to {client_address}: "
            f"{time_correction:+.3f} seconds"
        )

        client_connection.sendall(
            f"{time_correction:.3f}".encode()
        )

        client_connection.close()

    print("\n[SERVER] Synchronization complete.")

    print(
        f"[SERVER] New server time: "
        f"{server_time + server_correction:.3f}"
    )

    server_socket.close()

if __name__ == "__main__":
    main()
