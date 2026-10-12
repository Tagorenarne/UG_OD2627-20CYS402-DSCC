import socket
import time
import os
import sys
from datetime import datetime

MASTER_ID = os.getenv("MASTER_ID", "Master")
MASTER_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
SLAVES_CONFIG = os.getenv("SLAVES", "berkeley-slave1:6000,berkeley-slave2:6000,berkeley-slave3:6000,berkeley-slave4:6000")
ARTIFICIAL_DELAY = float(os.getenv("ARTIFICIAL_DELAY", "0.05"))
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "0"))

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

def parse_slaves(config_str):
    slaves = []
    for entry in config_str.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            host, port = entry.split(":")
            slaves.append((host, int(port)))
        else:
            slaves.append((entry, 6000))
    return slaves

def wait_for_slaves(slave_list, max_retries=30, delay=1.0):
    print(f"Waiting for {len(slave_list)} slaves to become reachable...", flush=True)
    ready = set()
    for attempt in range(max_retries):
        for host, port in slave_list:
            if (host, port) in ready:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                s.connect((host, port))
                s.close()
                ready.add((host, port))
                print(f" -> Slave {host}:{port} is online.", flush=True)
            except Exception:
                pass
        if len(ready) == len(slave_list):
            print("All slaves are connected and ready.\n", flush=True)
            return True
        time.sleep(delay)
    print(f"Warning: Only {len(ready)}/{len(slave_list)} slaves responded.", flush=True)
    return len(ready) > 0

def run_berkeley_sync(current_master_offset, slave_list):
    print("=" * 82, flush=True)
    print("                BERKELEY CLOCK SYNCHRONIZATION ALGORITHM                ", flush=True)
    print("=" * 82, flush=True)
    print(f"Master Coordinator : {MASTER_ID}", flush=True)
    print(f"Master Offset      : {current_master_offset:+.3f} s", flush=True)
    print(f"Master Logical Time: {format_time(time.time() + current_master_offset)}", flush=True)
    print(f"Slaves Count       : {len(slave_list)}", flush=True)
    print("-" * 82, flush=True)

    records = []

    # Phase 1: Poll each slave
    for host, port in slave_list:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            
            # Artificial network latency simulation if requested
            if ARTIFICIAL_DELAY > 0:
                time.sleep(ARTIFICIAL_DELAY)

            t1 = time.time() + current_master_offset
            s.connect((host, port))
            s.sendall("POLL\n".encode())

            response = s.recv(1024).decode().strip()
            t_slave = float(response)

            if ARTIFICIAL_DELAY > 0:
                time.sleep(ARTIFICIAL_DELAY)

            t2 = time.time() + current_master_offset

            rtt = t2 - t1
            delay = rtt / 2.0
            
            # Estimated slave time at master instant T2
            t_slave_est = t_slave + delay
            # Relative offset: how much slave differs from master at T2
            offset = t_slave_est - t2

            records.append({
                "host": host,
                "port": port,
                "socket": s,
                "t1": t1,
                "t_slave": t_slave,
                "t2": t2,
                "rtt": rtt,
                "delay": delay,
                "offset": offset
            })
        except Exception as e:
            print(f"Error polling slave {host}:{port}: {e}", flush=True)

    if not records:
        print("No slaves were successfully polled. Aborting round.", flush=True)
        return current_master_offset

    # Phase 2: Compute average offset
    # Master's offset relative to itself is 0.0
    all_offsets = [0.0] + [rec["offset"] for rec in records]
    avg_offset = sum(all_offsets) / len(all_offsets)

    # Master adjustment
    master_adj = avg_offset - 0.0

    # Phase 3: Send adjustments to slaves
    for rec in records:
        rec["adj"] = avg_offset - rec["offset"]
        s = rec["socket"]
        try:
            s.sendall(f"ADJUST:{rec['adj']}\n".encode())
            ack = s.recv(1024).decode().strip()
        except Exception as e:
            print(f"Error sending adjustment to {rec['host']}: {e}", flush=True)
        finally:
            s.close()

    # Phase 4: Output summary table
    print(f"{'Node':<16} {'Initial Clock':<16} {'RTT (ms)':<10} {'Offset (s)':<12} {'Adjustment (s)':<14} {'Sync Clock':<16}", flush=True)
    print("-" * 82, flush=True)

    master_before = time.time() + current_master_offset
    new_master_offset = current_master_offset + master_adj
    master_after = time.time() + new_master_offset

    print(f"{MASTER_ID:<16} {format_time(master_before):<16} {'-':<10} {'+0.000':<12} {master_adj:+14.4f} {format_time(master_after):<16}", flush=True)

    for rec in records:
        s_initial_clock = rec["t_slave"]
        s_sync_clock = s_initial_clock + rec["adj"]
        print(f"{rec['host']:<16} {format_time(s_initial_clock):<16} {round(rec['rtt']*1000, 2):<10.2f} {rec['offset']:+12.4f} {rec['adj']:+14.4f} {format_time(s_sync_clock):<16}", flush=True)

    print("-" * 82, flush=True)
    print(f"Average System Adjustment   : {avg_offset:+.4f} s", flush=True)
    print(f"Cluster Synchronized Clock  : {format_time(master_after)}", flush=True)
    print("=" * 82 + "\n", flush=True)

    return new_master_offset

def main():
    slaves = parse_slaves(SLAVES_CONFIG)
    print(f"Starting Berkeley Master coordinator...", flush=True)
    print(f"Target Slaves: {slaves}", flush=True)

    # Wait for slaves
    if not wait_for_slaves(slaves):
        sys.exit(1)

    # Initial stabilization pause
    time.sleep(2)

    current_offset = MASTER_OFFSET
    current_offset = run_berkeley_sync(current_offset, slaves)

    if SYNC_INTERVAL > 0:
        while True:
            time.sleep(SYNC_INTERVAL)
            current_offset = run_berkeley_sync(current_offset, slaves)
    else:
        print("Berkeley synchronization complete. Coordinator entering standby...", flush=True)
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    main()
