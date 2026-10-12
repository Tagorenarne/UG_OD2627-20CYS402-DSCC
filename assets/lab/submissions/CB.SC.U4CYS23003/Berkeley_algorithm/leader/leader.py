import socket
import time

HOST = "0.0.0.0"
PORT = 5000

FOLLOWERS = [
    ("follower1", 5001),
    ("follower2", 5002),
    ("follower3", 5003)
]


def get_time():
    return time.time()


def send_message(host, port, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode())

            response = s.recv(1024).decode()
            return response

    except Exception as e:
        print(f"Could not connect to {host}:{port} -> {e}")
        return None


print("Berkeley Clock Synchronization - Leader")
print("----------------------------------------")

while True:

    leader_time = get_time()

    print(f"\nLeader clock: {leader_time:.3f}")

    offsets = []

    # Ask followers for their clocks
    for host, port in FOLLOWERS:

        response = send_message(host, port, "GET_TIME")

        if response:

            follower_time = float(response)

            offset = follower_time - leader_time

            offsets.append((host, port, offset))

            print(
                f"{host}: {follower_time:.3f} "
                f"(offset: {offset:+.3f}s)"
            )

    if offsets:

        # Berkeley algorithm:
        # Ignore failed/unreachable nodes.
        total_offset = sum(offset for _, _, offset in offsets)

        average_offset = total_offset / (len(offsets) + 1)

        print(f"\nAverage offset: {average_offset:+.3f}s")

        # Adjustment for leader
        print(
            f"Leader adjustment: {average_offset:+.3f}s"
        )

        # Send adjustments to followers
        for host, port, offset in offsets:

            adjustment = average_offset - offset

            message = f"ADJUST {adjustment}"

            send_message(host, port, message)

            print(
                f"{host} adjustment: "
                f"{adjustment:+.3f}s"
            )

    else:
        print("No followers available.")

    time.sleep(10)