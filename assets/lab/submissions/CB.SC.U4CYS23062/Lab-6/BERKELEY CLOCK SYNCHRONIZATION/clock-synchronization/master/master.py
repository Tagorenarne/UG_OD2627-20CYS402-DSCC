import socket
import threading
import time
from datetime import datetime


HOST = "0.0.0.0"
PORT = 5000

clients = {}
final_clocks = {}

lock = threading.Lock()
final_condition = threading.Condition(lock)


def format_time(timestamp):
    return datetime.fromtimestamp(
        timestamp
    ).strftime("%H:%M:%S.%f")[:-3]


def handle_client(conn, addr):

    try:

        # ------------------------------------------
        # STEP 1: Receive initial clock
        # ------------------------------------------

        data = conn.recv(1024).decode()

        if data.startswith("CLOCK_REQUEST"):

            parts = data.split("|")

            client_id = parts[1]
            client_time = float(parts[2])

            # Record master's clock immediately when
            # request arrives.
            master_time = time.time()

            with lock:

                clients[client_id] = {
                    "time": client_time,
                    "master_time": master_time,
                    "connection": conn
                }

            print(
                f"Received from {client_id}: "
                f"{format_time(client_time)}"
            )

            # --------------------------------------
            # IMPORTANT:
            # Keep this connection open.
            # The master will later send the
            # correction through the same socket.
            # --------------------------------------

            while True:

                data = conn.recv(1024).decode()

                if not data:
                    break

                # ----------------------------------
                # STEP 2: Receive final clock
                # ----------------------------------

                if data.startswith("FINAL"):

                    parts = data.split("|")

                    client_id = parts[1]
                    final_time = float(parts[2])

                    # Record master's current time at
                    # the moment the final clock arrives.
                    final_master_time = time.time()

                    with lock:

                        final_clocks[client_id] = {
                            "client_time": final_time,
                            "master_time": final_master_time
                        }

                        final_condition.notify_all()

                    print(
                        f"Final clock received from "
                        f"{client_id}: "
                        f"{format_time(final_time)}"
                    )

                    conn.sendall(b"ACK")

                    break

    except Exception as e:

        print(
            f"Client connection error: {e}"
        )

    finally:

        # Only close after the complete
        # synchronization exchange.
        try:
            conn.close()
        except:
            pass


def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen(10)

    print("=" * 55)
    print("          BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 55)

    print(
        f"Master listening on port {PORT}"
    )

    print("Waiting for clients...")
    print()

    while True:

        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )

        thread.start()


def synchronize():

    print("Waiting for all clients...")

    # Allow all four clients to send their
    # initial clocks.
    time.sleep(8)

    with lock:
        client_data = clients.copy()

    if len(client_data) < 4:

        print(
            f"Only {len(client_data)} clients "
            f"responded."
        )

        print(
            "Synchronization cancelled."
        )

        return

    # ==========================================
    # INITIAL CLOCKS
    # ==========================================

    print()
    print("=" * 55)
    print("INITIAL CLOCKS")
    print("=" * 55)

    first_client = next(
        iter(client_data)
    )

    display_master_time = (
        client_data[first_client]["master_time"]
    )

    print(
        f"Master       : "
        f"{format_time(display_master_time)}"
    )

    for client_id, data in sorted(
        client_data.items()
    ):

        print(
            f"{client_id:<12}: "
            f"{format_time(data['time'])}"
        )

    # ==========================================
    # CLOCK OFFSETS
    # ==========================================

    offsets = {}

    for client_id, data in client_data.items():

        offsets[client_id] = (
            data["time"]
            - data["master_time"]
        )

    print()
    print("-" * 55)
    print("CLOCK OFFSETS")
    print("-" * 55)

    print(
        "Master       : +0.000 sec"
    )

    for client_id, offset in sorted(
        offsets.items()
    ):

        print(
            f"{client_id:<12}: "
            f"{offset:+.3f} sec"
        )

    # ==========================================
    # AVERAGE OFFSET
    # ==========================================

    all_offsets = (
        [0.0]
        + list(offsets.values())
    )

    average_offset = (
        sum(all_offsets)
        / len(all_offsets)
    )

    print()
    print(
        f"Average Offset: "
        f"{average_offset:+.3f} sec"
    )

    # ==========================================
    # CORRECTIONS
    # ==========================================

    print()
    print("-" * 55)
    print("CORRECTIONS")
    print("-" * 55)

    print(
        f"Master       : "
        f"{average_offset:+.3f} sec"
    )

    corrections = {}

    for client_id, offset in sorted(
        offsets.items()
    ):

        correction = (
            average_offset - offset
        )

        corrections[client_id] = correction

        print(
            f"{client_id:<12}: "
            f"{correction:+.3f} sec"
        )

    # ==========================================
    # SEND CORRECTIONS
    # ==========================================

    for client_id, correction in (
        corrections.items()
    ):

        try:

            conn = client_data[
                client_id
            ]["connection"]

            message = (
                f"CORRECTION|"
                f"{correction:.6f}"
            )

            conn.sendall(
                message.encode()
            )

        except Exception as e:

            print(
                f"Could not send correction "
                f"to {client_id}: {e}"
            )

    # ==========================================
    # WAIT FOR FINAL CLOCKS
    # ==========================================

    print()
    print(
        "Waiting for final synchronized clocks..."
    )

    # Wait until all four clients report their
    # corrected clocks.
    with final_condition:

        final_condition.wait_for(
            lambda: len(final_clocks) >= 4,
            timeout=10
        )

        final_data = final_clocks.copy()

    # ==========================================
    # FINAL SYNCHRONIZED CLOCKS
    # ==========================================

    print()
    print("-" * 55)
    print("FINAL SYNCHRONIZED CLOCKS")
    print("-" * 55)

    # Master corrected logical clock is measured
    # at approximately the same stage as the
    # final client measurements.
    current_master_time = (
        time.time()
        + average_offset
    )

    print(
        f"Master       : "
        f"{format_time(current_master_time)}"
    )

    for client_id in sorted(
        final_data.keys()
    ):

        client_final_time = (
            final_data[client_id]["client_time"]
        )

        master_at_receive = (
            final_data[client_id]["master_time"]
            + average_offset
        )

        error = (
            client_final_time
            - master_at_receive
        )

        print(
            f"{client_id:<12}: "
            f"{format_time(client_final_time)} "
            f"(Error: {error:+.3f}s)"
        )

    print()
    print("=" * 55)
    print("Synchronization complete!")
    print("=" * 55)


if __name__ == "__main__":

    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()

    synchronize()