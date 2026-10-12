import os
import socket
import time

MASTER_PORT = int(os.getenv("MASTER_PORT", "5000"))
MASTER_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

CLIENTS = os.getenv(
    "CLIENTS",
    "follower1,follower2,follower3,follower4"
).split(",")

CLIENT_PORT = 5001

# Nodes with an absolute offset larger than this value
# are treated as outliers.
OUTLIER_THRESHOLD = float(
    os.getenv("OUTLIER_THRESHOLD", "20")
)


def get_clock():
    return time.time() + MASTER_OFFSET


def send_request(client, message):
    """Send a request to a client."""

    try:
        with socket.create_connection(
            (client, CLIENT_PORT),
            timeout=5
        ) as sock:

            sock.sendall(message.encode())

            response = sock.recv(1024).decode().strip()

            return response

    except Exception as e:
        print(
            f"[MASTER] Could not contact {client}: {e}"
        )
        return None


def synchronize():
    global MASTER_OFFSET

    print("\n" + "=" * 75)
    print("           BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 75)

    # --------------------------------------------------
    # 1. Get master's clock
    # --------------------------------------------------

    master_clock = get_clock()

    print("\n[1] INITIAL CLOCKS")
    print("-" * 75)

    print(
        f"master   : {master_clock:.6f}"
    )

    clocks = {
        "master": master_clock
    }

    # --------------------------------------------------
    # 2. Poll clients
    # --------------------------------------------------

    print("\n[2] POLLING CLIENTS")
    print("-" * 75)

    for client in CLIENTS:

        response = None

        for attempt in range(10):

            response = send_request(
                client,
                "CLOCK_REQUEST"
            )

            if response:
                break

            print(
                f"[MASTER] Retrying {client} "
                f"({attempt + 1}/10)..."
            )

            time.sleep(1)

        if response:

            try:
                client_id, clock = response.split("|")

                clock = float(clock)

                clocks[client_id] = clock

                print(
                    f"{client_id:<10}: "
                    f"{clock:.6f}"
                )

            except Exception as e:

                print(
                    f"[MASTER] Invalid response "
                    f"from {client}: {e}"
                )

        else:

            print(
                f"{client:<10}: NO RESPONSE"
            )

    # --------------------------------------------------
    # 3. Calculate offsets
    # --------------------------------------------------

    print("\n[3] OFFSETS RELATIVE TO MASTER")
    print("-" * 75)

    offsets = {}

    for node, clock in clocks.items():

        offset = clock - master_clock

        offsets[node] = offset

        print(
            f"{node:<10}: "
            f"{offset:+.6f} seconds"
        )

    # --------------------------------------------------
    # 4. Detect outliers
    # --------------------------------------------------

    valid_offsets = {}
    excluded_offsets = {}

    for node, offset in offsets.items():

        if abs(offset) > OUTLIER_THRESHOLD:
            excluded_offsets[node] = offset
        else:
            valid_offsets[node] = offset

    print("\n[4] OUTLIER CHECK")
    print("-" * 75)

    print(
        f"Outlier threshold = "
        f"{OUTLIER_THRESHOLD:.2f} seconds"
    )

    if excluded_offsets:

        for node, offset in excluded_offsets.items():

            print(
                f"{node:<10}: EXCLUDED "
                f"({offset:+.6f} seconds)"
            )

    else:

        print("No outliers detected.")

    # --------------------------------------------------
    # 5. Calculate average offset
    # --------------------------------------------------

    average_offset = (
        sum(valid_offsets.values()) /
        len(valid_offsets)
    )

    print("\n[5] AVERAGE OFFSET")
    print("-" * 75)

    print(
        f"Average offset = "
        f"{average_offset:+.6f} seconds"
    )

    # --------------------------------------------------
    # 6. Calculate corrections
    # --------------------------------------------------

    print("\n[6] CORRECTIONS")
    print("-" * 75)

    corrections = {}

    for node, offset in valid_offsets.items():

        correction = average_offset - offset

        corrections[node] = correction

        print(
            f"{node:<10}: "
            f"{correction:+.6f} seconds"
        )

    # --------------------------------------------------
    # 7. Apply master's correction
    # --------------------------------------------------

    if "master" in corrections:

        MASTER_OFFSET += corrections["master"]

    print("\n[7] MASTER CORRECTION")
    print("-" * 75)

    print(
        f"Master correction = "
        f"{corrections.get('master', 0):+.6f} seconds"
    )

    # --------------------------------------------------
    # 8. Send corrections
    # --------------------------------------------------

    print("\n[8] SENDING CORRECTIONS")
    print("-" * 75)

    for client in CLIENTS:

        if client not in corrections:

            if client in excluded_offsets:

                print(
                    f"{client:<10}: "
                    f"EXCLUDED AS OUTLIER"
                )

            else:

                print(
                    f"{client:<10}: "
                    f"no correction"
                )

            continue

        correction = corrections[client]

        response = send_request(
            client,
            f"CORRECTION {correction}"
        )

        if response:

            print(
                f"{client:<10}: "
                f"{correction:+.6f} seconds"
            )

        else:

            print(
                f"{client:<10}: "
                f"correction failed"
            )

    time.sleep(1)

    # --------------------------------------------------
    # 9. Get final clocks
    # --------------------------------------------------

    print("\n[9] FINAL CLOCKS")
    print("-" * 75)

    final_clocks = {
        "master": get_clock()
    }

    print(
        f"{'master':<10}: "
        f"{final_clocks['master']:.6f}"
    )

    for client in CLIENTS:

        response = send_request(
            client,
            "FINAL_CLOCK"
        )

        if response:

            try:
                client_id, clock = response.split("|")

                clock = float(clock)

                final_clocks[client_id] = clock

                print(
                    f"{client_id:<10}: "
                    f"{clock:.6f}"
                )

            except Exception:
                pass

    # --------------------------------------------------
    # 10. Synchronization result
    # --------------------------------------------------

    valid_final_clocks = {
        node: clock
        for node, clock in final_clocks.items()
        if node in valid_offsets
    }

    if len(valid_final_clocks) > 1:

        minimum = min(
            valid_final_clocks.values()
        )

        maximum = max(
            valid_final_clocks.values()
        )

        synchronization_error = (
            maximum - minimum
        )

        print("\n[10] SYNCHRONIZATION RESULT")
        print("-" * 75)

        print(
            f"Minimum valid clock : "
            f"{minimum:.6f}"
        )

        print(
            f"Maximum valid clock : "
            f"{maximum:.6f}"
        )

        print(
            f"Synchronization error "
            f"(excluding outliers): "
            f"{synchronization_error:.6f} seconds"
        )

    print("\n" + "=" * 75)
    print("BERKELEY SYNCHRONIZATION COMPLETED")
    print("=" * 75)


def main():

    print(
        "[MASTER] Starting Berkeley Clock Synchronization"
    )

    print(
        f"[MASTER] Port: {MASTER_PORT}"
    )

    print(
        f"[MASTER] Outlier threshold: "
        f"{OUTLIER_THRESHOLD} seconds"
    )

    time.sleep(8)

    synchronize()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
