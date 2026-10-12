import os
import socket
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
CLIENT_PORT = int(os.getenv("CLIENT_PORT", "5001"))


def get_clock():
    return time.time() + CLOCK_OFFSET


def handle_request(conn):
    global CLOCK_OFFSET

    request = conn.recv(1024).decode().strip()

    if request == "CLOCK_REQUEST":
        current_clock = get_clock()

        response = f"{CLIENT_ID}|{current_clock:.6f}"
        conn.sendall(response.encode())

        print(
            f"[{CLIENT_ID}] Clock requested: "
            f"{current_clock:.6f}"
        )

    elif request.startswith("CORRECTION"):
        correction = float(request.split()[1])

        CLOCK_OFFSET += correction

        print(
            f"[{CLIENT_ID}] Correction received: "
            f"{correction:+.6f} seconds"
        )

        print(
            f"[{CLIENT_ID}] New clock offset: "
            f"{CLOCK_OFFSET:+.6f} seconds"
        )

        conn.sendall(b"CORRECTION_APPLIED")

    elif request == "FINAL_CLOCK":
        final_clock = get_clock()

        response = f"{CLIENT_ID}|{final_clock:.6f}"
        conn.sendall(response.encode())

        print(
            f"[{CLIENT_ID}] Final clock: "
            f"{final_clock:.6f}"
        )


def main():
    print("=" * 60)
    print(f"[{CLIENT_ID}] Berkeley client starting")
    print(f"[{CLIENT_ID}] Initial offset: {CLOCK_OFFSET:+.2f} seconds")
    print(f"[{CLIENT_ID}] Listening on port {CLIENT_PORT}")
    print("=" * 60)

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(("0.0.0.0", CLIENT_PORT))
    server.listen(5)

    while True:
        conn, address = server.accept()

        try:
            handle_request(conn)
        except Exception as e:
            print(f"[{CLIENT_ID}] Error: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
