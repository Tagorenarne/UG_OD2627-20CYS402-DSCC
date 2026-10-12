import socket
import json
import time


MASTER_HOST = "0.0.0.0"
MASTER_PORT = 5000

CLIENTS = {
    "client1": ("clock-client1", 5001),
    "client2": ("clock-client2", 5001),
    "client3": ("clock-client3", 5001),
    "client4": ("clock-client4", 5001),
}

# Master's own logical clock offset
MASTER_OFFSET = 0.0


def get_master_clock():
    """Return the master's current logical clock."""
    return time.time() + MASTER_OFFSET


def communicate_with_client(host, port, message):
    """Send a request to a client and receive its response."""

    try:
        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.settimeout(5)

        client_socket.connect((host, port))

        client_socket.sendall(
            json.dumps(message).encode()
        )

        data = client_socket.recv(4096)

        client_socket.close()

        if data:
            return json.loads(data.decode())

    except Exception as error:
        print(f"Connection error with {host}: {error}")

    return None


def request_clock(client_name, host, port):
    """Request the current clock from a client."""

    message = {
        "type": "CLOCK_REQUEST"
    }

    response = communicate_with_client(
        host,
        port,
        message
    )

    if response and response.get("type") == "CLOCK_RESPONSE":
        return response.get("clock")

    return None


def send_correction(client_name, host, port, correction):
    """Send a Berkeley clock correction to a client."""

    message = {
        "type": "CORRECTION",
        "correction": correction
    }

    response = communicate_with_client(
        host,
        port,
        message
    )

    return response


def run_berkeley_algorithm():
    global MASTER_OFFSET

    print()
    print("=" * 60)
    print("           BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Step 1: Get master's current clock
    # ---------------------------------------------------------

    master_clock = get_master_clock()

    clocks = {
        "master": master_clock
    }

    print()
    print("INITIAL CLOCKS")
    print("-" * 60)
    print(f"Master       : {master_clock:.2f}")

    # ---------------------------------------------------------
    # Step 2: Poll all clients
    # ---------------------------------------------------------

    print()
    print("POLLING CLIENTS")
    print("-" * 60)

    for client_name, (host, port) in CLIENTS.items():

        print(
            f"MASTER -> {client_name}: CLOCK_REQUEST"
        )

        clock = request_clock(
            client_name,
            host,
            port
        )

        if clock is not None:

            clocks[client_name] = clock

            print(
                f"{client_name} -> MASTER: "
                f"{clock:.2f}"
            )

        else:

            print(
                f"{client_name}: No response"
            )

    # ---------------------------------------------------------
    # Step 3: Calculate offsets relative to master
    # ---------------------------------------------------------

    print()
    print("CLOCK OFFSETS")
    print("-" * 60)

    offsets = {}

    for node, clock in clocks.items():

        offset = clock - master_clock

        offsets[node] = offset

        print(
            f"{node:<12}: {offset:+.2f} sec"
        )

    # ---------------------------------------------------------
    # Step 4: Calculate average offset
    # ---------------------------------------------------------

    average_offset = sum(offsets.values()) / len(offsets)

    print()
    print("-" * 60)

    print(
        f"Average Offset: "
        f"{average_offset:+.2f} sec"
    )

    # ---------------------------------------------------------
    # Step 5: Calculate corrections
    # ---------------------------------------------------------

    print()
    print("CORRECTIONS")
    print("-" * 60)

    corrections = {}

    for node, offset in offsets.items():

        correction = average_offset - offset

        corrections[node] = correction

        print(
            f"{node:<12}: "
            f"{correction:+.2f} sec"
        )

    # ---------------------------------------------------------
    # Step 6: Apply master's correction
    # ---------------------------------------------------------

    MASTER_OFFSET += corrections["master"]

    print()
    print(
        f"Master correction applied: "
        f"{corrections['master']:+.2f} sec"
    )

    # ---------------------------------------------------------
    # Step 7: Send corrections to clients
    # ---------------------------------------------------------

    print()
    print("SENDING CORRECTIONS")
    print("-" * 60)

    for client_name, (host, port) in CLIENTS.items():

        if client_name not in corrections:
            continue

        correction = corrections[client_name]

        print(
            f"MASTER -> {client_name}: "
            f"{correction:+.2f} sec"
        )

        send_correction(
            client_name,
            host,
            port,
            correction
        )

    # Give clients a moment to apply corrections
    time.sleep(1)

    # ---------------------------------------------------------
    # Step 8: Display final clocks
    # ---------------------------------------------------------

    print()
    print("FINAL CLOCKS")
    print("-" * 60)

    final_master_clock = get_master_clock()

    print(
        f"Master       : "
        f"{final_master_clock:.2f}"
    )

    for client_name, (host, port) in CLIENTS.items():

        final_clock = request_clock(
            client_name,
            host,
            port
        )

        if final_clock is not None:

            print(
                f"{client_name:<12}: "
                f"{final_clock:.2f}"
            )

    print()
    print("=" * 60)
    print("        BERKELEY SYNCHRONIZATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":

    print("Starting Berkeley Master/Coordinator...")

    # Give Docker clients time to start
    time.sleep(5)

    run_berkeley_algorithm()