import socket
import time

HOST = "0.0.0.0"
PORT = 5000

# Master's logical clock offset
master_offset = 0.0


def get_master_clock():
    """Return master's current logical clock."""
    return time.time() + master_offset


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


def main():
    global master_offset

    clients = {}

    print("=" * 60)
    print("========== BERKELEY CLOCK SYNCHRONIZATION ==========")
    print("=" * 60)

    # Create TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"Master listening on port {PORT}...")
    print("Waiting for 4 clients...\n")

    # Receive clocks from four clients
    while len(clients) < 4:

        conn, address = server.accept()

        try:
            data = conn.recv(1024).decode()

            if data.startswith("CLOCK"):
                parts = data.split("|")

                client_id = parts[1]
                client_clock = float(parts[2])

                clients[client_id] = {
                    "clock": client_clock,
                    "connection": conn
                }

                print(
                    f"Received clock from {client_id}: "
                    f"{client_clock:.2f}"
                )

        except Exception as e:
            print(f"Error receiving client data: {e}")
            conn.close()

    # Get master's current logical clock
    master_clock = get_master_clock()

    # --------------------------------------------------
    # INITIAL CLOCKS
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("INITIAL CLOCKS")
    print("=" * 60)

    print(f"Master       : {format_time(master_clock)}")

    for client_id, data in clients.items():
        print(
            f"{client_id:<13}: "
            f"{format_time(data['clock'])}"
        )

    # --------------------------------------------------
    # CALCULATE OFFSETS
    # --------------------------------------------------

    offsets = {}

    # Master is the reference
    offsets["master"] = 0.0

    for client_id, data in clients.items():
        offsets[client_id] = data["clock"] - master_clock

    print("\n" + "-" * 60)
    print("CLOCK OFFSETS")
    print("-" * 60)

    print(f"Master       : {offsets['master']:+.2f} sec")

    for client_id in clients:
        print(
            f"{client_id:<13}: "
            f"{offsets[client_id]:+.2f} sec"
        )

    # --------------------------------------------------
    # CALCULATE AVERAGE OFFSET
    # --------------------------------------------------

    total_offset = sum(offsets.values())
    average_offset = total_offset / len(offsets)

    print("\n" + "-" * 60)
    print(f"Average Offset: {average_offset:+.2f} sec")
    print("-" * 60)

    # --------------------------------------------------
    # CALCULATE CORRECTIONS
    # --------------------------------------------------

    corrections = {}

    print("\nCORRECTIONS")

    master_correction = average_offset - offsets["master"]

    print(
        f"Master       : "
        f"{master_correction:+.2f} sec"
    )

    for client_id in clients:

        correction = (
            average_offset
            - offsets[client_id]
        )

        corrections[client_id] = correction

        print(
            f"{client_id:<13}: "
            f"{correction:+.2f} sec"
        )

    # --------------------------------------------------
    # APPLY MASTER CORRECTION
    # --------------------------------------------------

    master_offset += master_correction

    # --------------------------------------------------
    # SEND CORRECTIONS
    # --------------------------------------------------

    print("\nSending corrections to clients...\n")

    for client_id, data in clients.items():

        correction = corrections[client_id]

        try:
            message = f"CORRECTION|{correction}"

            data["connection"].sendall(
                message.encode()
            )

            data["connection"].close()

        except Exception as e:
            print(
                f"Could not send correction to "
                f"{client_id}: {e}"
            )

    # --------------------------------------------------
    # FINAL SYNCHRONIZED CLOCKS
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL SYNCHRONIZED CLOCKS")
    print("=" * 60)

    final_master_clock = (
        master_clock + master_correction
    )

    print(
        f"Master       : "
        f"{format_time(final_master_clock)}"
    )

    for client_id, data in clients.items():

        final_clock = (
            data["clock"]
            + corrections[client_id]
        )

        print(
            f"{client_id:<13}: "
            f"{format_time(final_clock)}"
        )

    print("\n" + "=" * 60)
    print("Synchronization completed.")
    print("=" * 60)

    server.close()


if __name__ == "__main__":
    main()