#!/usr/bin/env python3
import socket
import time
from datetime import datetime
import json
import os

SERVER_HOST = os.environ.get('SERVER_HOST', 'time-server')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 8888))
# Simulated local clock drift in seconds (to vividly demonstrate synchronization)
INITIAL_DRIFT = float(os.environ.get('SIMULATED_DRIFT', '12.345678'))
ROUNDS = int(os.environ.get('ROUNDS', '5'))
INTERVAL = float(os.environ.get('INTERVAL', '3.0'))

class VirtualClock:
    def __init__(self, initial_drift: float):
        self.drift = initial_drift

    def now(self) -> float:
        return time.time() + self.drift

    def adjust(self, offset: float):
        self.drift += offset

def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

def run_client():
    print("==================================================")
    print("  Cristian's Clock Synchronization Algorithm")
    print("==================================================")
    print(f"[*] Target Server : {SERVER_HOST}:{SERVER_PORT}")
    print(f"[*] Initial Clock Drift : {INITIAL_DRIFT:+.6f} seconds")
    print(f"[*] Total Rounds  : {ROUNDS}")
    print("==================================================\n")

    virtual_clock = VirtualClock(INITIAL_DRIFT)

    # Wait for server container to become ready
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.connect((SERVER_HOST, SERVER_PORT))
            test_socket.close()
            print(f"[+] Successfully connected to time server at {SERVER_HOST}:{SERVER_PORT}\n")
            break
        except Exception:
            if attempt == max_retries:
                print(f"[-] Could not connect to {SERVER_HOST}:{SERVER_PORT} after {max_retries} attempts. Exiting.")
                return
            print(f"[*] Waiting for server to be reachable (attempt {attempt}/{max_retries})...")
            time.sleep(1.5)

    for i in range(1, ROUNDS + 1):
        print(f"--- [Round {i}/{ROUNDS}] ---")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))

            # 1. Record local time before sending request (T0)
            t0 = virtual_clock.now()
            t0_str = format_time(t0)

            # Send time request
            s.sendall(b'TIME_REQ')

            # Receive server timestamp
            response_bytes = s.recv(1024)
            
            # 2. Record local time upon receiving response (T1)
            t1 = virtual_clock.now()
            t1_str = format_time(t1)
            
            s.close()

            response = json.loads(response_bytes.decode('utf-8'))
            t_server = response['server_time']
            t_server_str = response['server_time_str']

            # 3. Calculate Round-Trip Time (RTT)
            rtt = t1 - t0
            
            # 4. Estimate one-way network latency
            latency = rtt / 2.0

            # 5. Calculate synchronized time according to Cristian's Algorithm
            # T_sync = T_server + (RTT / 2)
            t_sync = t_server + latency
            t_sync_str = format_time(t_sync)

            # 6. Calculate clock offset (difference between synchronized time and client's clock at T1)
            offset = t_sync - t1

            print(f"  T0 (Client Request Sent)  : {t0_str} ({t0:.6f})")
            print(f"  T_server (Server Timestamp): {t_server_str} ({t_server:.6f})")
            print(f"  T1 (Client Response Recv) : {t1_str} ({t1:.6f})")
            print(f"  Round Trip Time (RTT)     : {rtt * 1000:.3f} ms")
            print(f"  Estimated 1-way Latency   : {latency * 1000:.3f} ms")
            print(f"  Calculated Clock Offset   : {offset:+.6f} seconds")
            print(f"  Client Time Before Sync   : {t1_str}")
            print(f"  Client Time After Sync    : {t_sync_str}")

            # Adjust virtual clock
            virtual_clock.adjust(offset)
            print(f"  Adjustment Applied        : {offset:+.6f}s")
            print(f"  Verified Client Clock Now : {format_time(virtual_clock.now())}")
            print("--------------------------------------------------\n")

        except Exception as e:
            print(f"[-] Error during synchronization round {i}: {e}")

        if i < ROUNDS:
            time.sleep(INTERVAL)

    print("[*] Cristian's Algorithm synchronization demonstration completed.")

if __name__ == '__main__':
    run_client()
