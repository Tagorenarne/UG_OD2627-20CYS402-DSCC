import time
import requests

CLIENTS = {
    "client1": "http://clock-client1:5000",
    "client2": "http://clock-client2:5000",
    "client3": "http://clock-client3:5000",
    "client4": "http://clock-client4:5000"
}

MASTER_OFFSET = 0.0


def get_master_clock():
    return time.time() + MASTER_OFFSET


def get_client_clock(client_url):
    response = requests.get(
        client_url + "/clock",
        timeout=5
    )

    response.raise_for_status()

    data = response.json()

    return data["clock"]


def send_correction(client_url, correction):
    response = requests.post(
        client_url + "/correct",
        json={
            "correction": correction
        },
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def format_clock(timestamp):
    return time.strftime(
        "%H:%M:%S",
        time.localtime(timestamp)
    ) + f".{int((timestamp % 1) * 10)}"


def synchronize():

    global MASTER_OFFSET

    print("\n")
    print("=" * 60)
    print("          BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 60)

    # --------------------------------------------
    # STEP 1: Get master clock
    # --------------------------------------------

    master_clock = get_master_clock()

    clocks = {
        "master": master_clock
    }

    print("\nInitial Clocks")
    print("-" * 60)

    print(
        f"Master       : {format_clock(master_clock)}"
    )

    # --------------------------------------------
    # STEP 2: Poll clients
    # --------------------------------------------

    for client_id, client_url in CLIENTS.items():

        try:
            clock = get_client_clock(client_url)

            clocks[client_id] = clock

            print(
                f"{client_id.capitalize():12}: "
                f"{format_clock(clock)}"
            )

        except Exception as e:

            print(
                f"{client_id.capitalize():12}: ERROR - {e}"
            )

    # --------------------------------------------
    # STEP 3: Calculate offsets
    # --------------------------------------------

    print("\n")
    print("Clock Offsets")
    print("-" * 60)

    offsets = {}

    master_clock = clocks["master"]

    for node, clock in clocks.items():

        offset = clock - master_clock

        offsets[node] = offset

        print(
            f"{node.capitalize():12}: "
            f"{offset:+.2f} sec"
        )

    # --------------------------------------------
    # STEP 4: Calculate average offset
    # --------------------------------------------

    average_offset = sum(offsets.values()) / len(offsets)

    print("\n")
    print(
        f"Average Offset: "
        f"{average_offset:+.2f} sec"
    )

    # --------------------------------------------
    # STEP 5: Calculate corrections
    # --------------------------------------------

    print("\n")
    print("Corrections")
    print("-" * 60)

    corrections = {}

    for node, offset in offsets.items():

        correction = average_offset - offset

        corrections[node] = correction

        print(
            f"{node.capitalize():12}: "
            f"{correction:+.2f} sec"
        )

    # --------------------------------------------
    # STEP 6: Correct master
    # --------------------------------------------

    MASTER_OFFSET += corrections["master"]

    # --------------------------------------------
    # STEP 7: Correct clients
    # --------------------------------------------

    print("\nApplying corrections...")

    for client_id, client_url in CLIENTS.items():

        try:

            result = send_correction(
                client_url,
                corrections[client_id]
            )

            print(
                f"{client_id.capitalize():12}: "
                f"{result['correction']:+.2f} sec"
            )

        except Exception as e:

            print(
                f"{client_id.capitalize():12}: "
                f"ERROR - {e}"
            )

    # --------------------------------------------
    # STEP 8: Display final clocks
    # --------------------------------------------

    time.sleep(1)

    final_master_clock = get_master_clock()

    print("\n")
    print("Final Clocks")
    print("-" * 60)

    print(
        f"Master       : "
        f"{format_clock(final_master_clock)}"
    )

    final_clocks = {
        "master": final_master_clock
    }

    for client_id, client_url in CLIENTS.items():

        try:

            clock = get_client_clock(client_url)

            final_clocks[client_id] = clock

            print(
                f"{client_id.capitalize():12}: "
                f"{format_clock(clock)}"
            )

        except Exception as e:

            print(
                f"{client_id.capitalize():12}: ERROR"
            )

    # --------------------------------------------
    # STEP 9: Calculate synchronization error
    # --------------------------------------------

    print("\n")
    print("Synchronization Error")
    print("-" * 60)

    reference = final_master_clock

    for node, clock in final_clocks.items():

        error = abs(clock - reference)

        print(
            f"{node.capitalize():12}: "
            f"{error:.4f} sec"
        )

    print("\n")
    print("=" * 60)


if __name__ == "__main__":

    print("Waiting for clients...")

    time.sleep(5)

    synchronize()

    print("\nSynchronization completed.")