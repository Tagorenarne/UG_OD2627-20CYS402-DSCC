import socket
import time
import os

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

MASTER_HOST = "clock-master"
MASTER_PORT = 5000

start_time = time.time()


def get_clock():
    elapsed = time.time() - start_time
    return elapsed + CLOCK_OFFSET


print("\n==========================================")
print("       CRISTIAN'S ALGORITHM")
print("==========================================")

print(f"Client ID     : {CLIENT_ID}")
print(f"Clock Offset  : {CLOCK_OFFSET:+.2f} sec")

# Wait for master to start
time.sleep(5)

# ------------------------------------------
# Initial clock
# ------------------------------------------

initial_clock = get_clock()

print(f"\nInitial Clock : {initial_clock:.3f}")

# ------------------------------------------
# Step 1: T1
# ------------------------------------------

T1 = get_clock()

# ------------------------------------------
# Step 2: Send request
# ------------------------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((MASTER_HOST, MASTER_PORT))

sock.send(b"TIME_REQUEST")

# ------------------------------------------
# Step 3: Receive master time
# ------------------------------------------

data = sock.recv(1024).decode()

# ------------------------------------------
# Step 4: T2
# ------------------------------------------

T2 = get_clock()

sock.close()

master_time = float(data)

# ------------------------------------------
# Step 5: RTT
# ------------------------------------------

RTT = T2 - T1

# ------------------------------------------
# Step 6: Estimated delay
# ------------------------------------------

estimated_delay = RTT / 2

# ------------------------------------------
# Step 7: Corrected clock
# ------------------------------------------

corrected_clock = master_time + estimated_delay

# ------------------------------------------
# Final error
# ------------------------------------------

final_error = corrected_clock - master_time

# ------------------------------------------
# Display results
# ------------------------------------------

print("\n------------------------------------------")

print(f"T1                : {T1:.3f}")
print(f"Master Time       : {master_time:.3f}")
print(f"T2                : {T2:.3f}")

print("\n------------------------------------------")

print(f"RTT               : {RTT * 1000:.2f} ms")
print(f"Estimated Delay   : {estimated_delay * 1000:.2f} ms")

print("\n------------------------------------------")

print(f"Corrected Clock   : {corrected_clock:.3f}")
print(f"Final Error       : {final_error * 1000:.2f} ms")

print("==========================================")
