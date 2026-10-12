import socket
import datetime
import time
import os
import threading


# ============================================================
# MASTER CONFIGURATION
# ============================================================

HOST = "0.0.0.0"

PORT = int(
    os.getenv("MASTER_PORT", "5000")
)

# Delay is specified in milliseconds
NETWORK_DELAY_MS = float(
    os.getenv("NETWORK_DELAY", "0")
)

NETWORK_DELAY_SECONDS = NETWORK_DELAY_MS / 1000.0

# Simulate approximately symmetric delay
HALF_DELAY = NETWORK_DELAY_SECONDS / 2


# ============================================================
# MASTER CLOCK
# ============================================================

def get_master_time():
    return datetime.datetime.now()


# ============================================================
# HANDLE ONE CLIENT
# ============================================================

def handle_client(connection, address):

    try:

        request = connection.recv(1024).decode().strip()

        print(
            f"[MASTER] Request from "
            f"{address[0]}:{address[1]} -> {request}"
        )

        if request == "TIME_REQUEST":

            # ------------------------------------------------
            # Simulate delay before the master timestamp
            # ------------------------------------------------

            if HALF_DELAY > 0:
                time.sleep(HALF_DELAY)

            # ------------------------------------------------
            # Master timestamp
            # ------------------------------------------------

            master_time = get_master_time()

            # ------------------------------------------------
            # Simulate delay after the timestamp
            # ------------------------------------------------

            if HALF_DELAY > 0:
                time.sleep(HALF_DELAY)

            # ------------------------------------------------
            # Send master time
            # ------------------------------------------------

            response = master_time.isoformat()

            connection.sendall(
                response.encode()
            )

            print(
                "[MASTER] Sent time:",
                master_time.strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )
            )

    except Exception as error:

        print(
            "[MASTER] Error:",
            error
        )

    finally:

        connection.close()


# ============================================================
# CREATE TCP SERVER
# ============================================================

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

server.listen(20)


# ============================================================
# MASTER INFORMATION
# ============================================================

print()
print("=" * 60)
print("                 CRISTIAN'S TIME MASTER")
print("=" * 60)

print(
    f"Listening on port : {PORT}"
)

print(
    f"Artificial delay  : {NETWORK_DELAY_MS:.0f} ms"
)

print(
    "Delay model       : approximately symmetric"
)

print(
    "Status            : Waiting for clients..."
)

print("=" * 60)


# ============================================================
# ACCEPT CLIENTS
# ============================================================

while True:

    connection, address = server.accept()

    # Handle each client independently.
    client_thread = threading.Thread(
        target=handle_client,
        args=(connection, address)
    )

    client_thread.daemon = True

    client_thread.start()
