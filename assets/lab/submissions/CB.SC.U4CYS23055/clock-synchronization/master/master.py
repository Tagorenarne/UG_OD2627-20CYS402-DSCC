import socket
import time
import os

MASTER_PORT = 5000
EXPECTED_CLIENTS = 4

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

start_time = time.time()


def get_logical_clock():
    return time.time() - start_time + CLOCK_OFFSET


def format_clock(seconds):
    seconds = seconds % 86400

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:04.1f}"


def start_master():

    print("======================================")
    print("     BERKELEY CLOCK SYNCHRONIZATION")
    print("======================================")

    print(f"Master Offset : {CLOCK_OFFSET:+.1f} seconds")

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        ("0.0.0.0", MASTER_PORT)
    )

    server_socket.listen(5)

    print(f"\nMaster listening on port {MASTER_PORT}")

    while True:

        print("\nWaiting for client connections...")

        client_data = {}

        # ----------------------------------
        # Step 1: Collect clocks
        # ----------------------------------

        while len(client_data) < EXPECTED_CLIENTS:

            connection, address = server_socket.accept()

            connection.sendall(b"CLOCK_REQUEST")

            data = connection.recv(1024).decode()

            if data:

                try:

                    client_id, clock_value = data.split("|")

                    client_clock = float(clock_value)

                    client_data[client_id] = {
                        "clock": client_clock,
                        "connection": connection
                    }

                    print(
                        f"Received from {client_id}: "
                        f"{format_clock(client_clock)}"
                    )

                except ValueError:

                    print("Invalid clock data received.")

                    connection.close()

        # ----------------------------------
        # Step 2: Get master's clock
        # ----------------------------------

        master_clock = get_logical_clock()

        # ----------------------------------
        # Step 3: Display initial clocks
        # ----------------------------------

        print("\n======================================")
        print("INITIAL CLOCKS")
        print("======================================")

        print(
            f"Master : {format_clock(master_clock)}"
        )

        for client_id, data in client_data.items():

            print(
                f"{client_id} : "
                f"{format_clock(data['clock'])}"
            )

        # ----------------------------------
        # Step 4: Calculate offsets
        # ----------------------------------

        offsets = {}

        offsets["Master"] = 0.0

        for client_id, data in client_data.items():

            offsets[client_id] = (
                data["clock"] - master_clock
            )

        print("\n======================================")
        print("CLOCK OFFSETS")
        print("======================================")

        for node, offset in offsets.items():

            print(
                f"{node:<8}: "
                f"{offset:+.2f} seconds"
            )

        # ----------------------------------
        # Step 5: Calculate average offset
        # ----------------------------------

        total_offset = sum(offsets.values())

        average_offset = (
            total_offset / len(offsets)
        )

        print("\n======================================")
        print("AVERAGE OFFSET")
        print("======================================")

        print(
            f"Average Offset: "
            f"{average_offset:+.2f} seconds"
        )

        # ----------------------------------
        # Step 6: Calculate corrections
        # ----------------------------------

        corrections = {}

        for node, offset in offsets.items():

            corrections[node] = (
                average_offset - offset
            )

        print("\n======================================")
        print("CORRECTIONS")
        print("======================================")

        for node, correction in corrections.items():

            print(
                f"{node:<8}: "
                f"{correction:+.2f} seconds"
            )

        # ----------------------------------
        # Step 7: Send corrections
        # ----------------------------------

        print("\n======================================")
        print("SENDING CORRECTIONS")
        print("======================================")

        for client_id, data in client_data.items():

            correction = corrections[client_id]

            message = (
                f"CORRECTION|{correction}"
            )

            data["connection"].sendall(
                message.encode()
            )

            print(
                f"Sent to {client_id}: "
                f"{correction:+.2f} seconds"
            )

            data["connection"].close()

        # ----------------------------------
        # Step 8: Apply master's correction
        # ----------------------------------

        master_correction = corrections["Master"]

        final_master_clock = (
            master_clock + master_correction
        )

        # ----------------------------------
        # Step 9: Display final clocks
        # ----------------------------------

        print("\n======================================")
        print("FINAL SYNCHRONIZED CLOCKS")
        print("======================================")

        print(
            f"Master : "
            f"{format_clock(final_master_clock)}"
        )

        for client_id, data in client_data.items():

            client_clock = data["clock"]

            correction = corrections[client_id]

            final_clock = (
                client_clock + correction
            )

            print(
                f"{client_id} : "
                f"{format_clock(final_clock)}"
            )

        print("\n======================================")
        print("SYNCHRONIZATION COMPLETE")
        print("======================================")


if __name__ == "__main__":
    start_master()