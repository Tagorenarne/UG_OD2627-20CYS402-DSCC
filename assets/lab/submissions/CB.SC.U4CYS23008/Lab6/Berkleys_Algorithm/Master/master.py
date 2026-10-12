import socket
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# Configuration
# ==========================================

HOST = "0.0.0.0"
PORT = int(os.getenv("MASTER_PORT", "5000"))
MASTER_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

CLIENTS = ["client1", "client2", "client3", "client4"]
TIMEOUT = float(os.getenv("CLIENT_TIMEOUT", "5"))

# Optional outlier filtering
EXCLUDE_OUTLIERS = os.getenv("EXCLUDE_OUTLIERS", "false").lower() == "true"
OUTLIER_THRESHOLD = float(os.getenv("OUTLIER_THRESHOLD", "60"))

IST = ZoneInfo("Asia/Kolkata")


# ==========================================
# Logical Clock
# ==========================================

def logical_clock():
    return time.time() + MASTER_OFFSET


def format_clock(timestamp):
    return datetime.fromtimestamp(
        timestamp, IST
    ).strftime("%H:%M:%S.%f")[:-3]


def send_message(conn, message):
    conn.sendall((message + "\n").encode("utf-8"))


def receive_message(conn):
    buffer = ""

    while "\n" not in buffer:
        data = conn.recv(4096)

        if not data:
            raise ConnectionError("Client disconnected")

        buffer += data.decode("utf-8")

    message, _ = buffer.split("\n", 1)
    return message.strip()


# ==========================================
# Main Berkeley Algorithm
# ==========================================

def main():
    global MASTER_OFFSET

    print("=" * 60, flush=True)
    print("BERKELEY CLOCK SYNCHRONIZATION", flush=True)
    print("=" * 60, flush=True)
    print(f"Master started on port {PORT}", flush=True)
    print("Time Zone: IST (Asia/Kolkata)", flush=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    server.settimeout(1)

    connections = {}
    start_time = time.time()

    print("Waiting for clients...", flush=True)

    # Accept the four clients.
    while len(connections) < len(CLIENTS):
        try:
            conn, address = server.accept()
            conn.settimeout(TIMEOUT)

            try:
                hello = receive_message(conn)
                parts = hello.split("|")

                if len(parts) != 2 or parts[0] != "HELLO":
                    conn.close()
                    continue

                client_id = parts[1]

                if client_id not in CLIENTS or client_id in connections:
                    conn.close()
                    continue

                connections[client_id] = conn
                print(
                    f"Connected: {client_id} from {address}",
                    flush=True
                )

            except (OSError, ConnectionError):
                conn.close()

        except socket.timeout:
            pass

        if time.time() - start_time > 60:
            print("Timed out waiting for all clients.", flush=True)
            for conn in connections.values():
                conn.close()
            server.close()
            return

    try:
        while True:
            print("\n" + "=" * 60, flush=True)
            print("BERKELEY SYNCHRONIZATION ROUND", flush=True)
            print("=" * 60, flush=True)

            # Poll all clients and collect their logical clock readings.
            readings = {"master": logical_clock()}
            initial_master_offset = MASTER_OFFSET

            for client_id, conn in connections.items():
                try:
                    send_message(conn, "CLOCK_REQUEST")
                    response = receive_message(conn)
                    parts = response.split("|")

                    if len(parts) != 3 or parts[0] != "CLOCK_RESPONSE":
                        raise ValueError("Invalid clock response")

                    if parts[1] != client_id:
                        raise ValueError("Client ID mismatch")

                    readings[client_id] = float(parts[2])

                except (OSError, ValueError, ConnectionError, socket.timeout) as e:
                    print(f"{client_id} did not respond: {e}", flush=True)

            # Use the master's current clock as the reference.
            reference = readings["master"]
            offsets = {
                node: clock - reference
                for node, clock in readings.items()
            }

            print("\nInitial Clocks", flush=True)
            for node, clock in readings.items():
                print(f"{node:12}: {format_clock(clock)}", flush=True)

            print("\nClock Offsets (relative to master)", flush=True)
            for node, offset in offsets.items():
                print(f"{node:12}: {offset:+.3f} seconds", flush=True)

            # Optional enhancement: exclude clients with large offsets.
            included = dict(offsets)

            if EXCLUDE_OUTLIERS:
                included = {
                    node: offset
                    for node, offset in offsets.items()
                    if node == "master"
                    or abs(offset) <= OUTLIER_THRESHOLD
                }

                excluded = set(offsets) - set(included)
                print(
                    f"\nExcluded outliers: {sorted(excluded) or 'None'}",
                    flush=True
                )

            average_offset = sum(included.values()) / len(included)

            print(
                f"\nAverage Offset: {average_offset:+.3f} seconds",
                flush=True
            )

            # The correction moves each participating clock to the
            # average time. Excluded clients are not corrected.
            corrections = {
                node: average_offset - offset
                for node, offset in offsets.items()
                if node in included
            }

            print("\nCorrections", flush=True)
            for node in offsets:
                if node in corrections:
                    print(
                        f"{node:12}: {corrections[node]:+.3f} seconds",
                        flush=True
                    )
                else:
                    print(f"{node:12}: EXCLUDED", flush=True)

            # Send corrections to the clients.
            for client_id, conn in connections.items():
                if client_id not in corrections:
                    continue

                try:
                    send_message(
                        conn,
                        f"CORRECTION|{corrections[client_id]:.9f}"
                    )
                except (OSError, ConnectionError):
                    print(
                        f"Failed to send correction to {client_id}",
                        flush=True
                    )

            # Apply the master's correction too.
            MASTER_OFFSET += corrections.get("master", 0.0)

            print("\nFinal Clocks (approximate)", flush=True)
            final_master = logical_clock()
            print(
                f"{'master':12}: {format_clock(final_master)}",
                flush=True
            )

            for client_id, old_clock in readings.items():
                if client_id == "master":
                    continue

                if client_id in corrections:
                    corrected = old_clock + corrections[client_id]
                    print(
                        f"{client_id:12}: {format_clock(corrected)}",
                        flush=True
                    )
                else:
                    print(
                        f"{client_id:12}: unchanged (outlier)",
                        flush=True
                    )

            print("\nNext synchronization in 30 seconds.", flush=True)
            time.sleep(30)

    except KeyboardInterrupt:
        print("Master stopped.", flush=True)

    finally:
        for conn in connections.values():
            conn.close()
        server.close()


if __name__ == "__main__":
    main()