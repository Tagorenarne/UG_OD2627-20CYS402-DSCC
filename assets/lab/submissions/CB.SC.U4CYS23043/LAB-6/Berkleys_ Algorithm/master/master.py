import json
import os
import socket
import time
from datetime import datetime, timezone

INITIAL_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))
CLIENT_CONFIG = os.environ.get("CLIENTS", "") 
WAIT_INTERVAL = float(os.environ.get("POLL_DELAY", "3"))
FILTER_ENABLED = os.environ.get("OUTLIER_FILTER", "false").lower() == "true"
MAX_OFFSET = float(os.environ.get("OUTLIER_THRESHOLD", "15"))


def get_clients(config: str):
    client_list = []
    for item in config.split(","):
        item = item.strip()
        if not item:
            continue
        hostname, port_num = item.split(":")
        client_list.append((hostname, int(port_num)))
    return client_list


def communicate(host, port, request, timeout=5):
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.sendall((json.dumps(request) + "\n").encode())
        response_file = connection.makefile("r")
        return json.loads(response_file.readline())


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%H:%M:%S.%f")[:-3]


def print_separator():
    print("-" * 44, flush=True)


def main():
    global INITIAL_OFFSET
    current_offset = INITIAL_OFFSET
    client_addresses = get_clients(CLIENT_CONFIG)

    print("========== BERKELEY ALGORITHM ==========\n", flush=True)
    print(f"Waiting {WAIT_INTERVAL:.0f}s for client containers to come up...\n", flush=True)
    time.sleep(WAIT_INTERVAL)

    def get_master_clock():
        return time.time() + current_offset

    # initial clocks
    print("Initial Clocks\n", flush=True)
    master_start = get_master_clock()
    print(f"Master       : {format_time(master_start)}", flush=True)

    client_records = {}  
    for hostname, port_num in client_addresses:
        try:
            response = communicate(hostname, port_num, {"cmd": "CLOCK_REQUEST"})
            client_name = response.get("client_id", hostname)
            client_records[client_name] = {"host": hostname, "port": port_num, "time": response["time"]}
            print(f"{client_name:<13}: {format_time(response['time'])}", flush=True)
        except Exception as error:
            print(f"{hostname:<13}: UNREACHABLE ({error})", flush=True)

    print()
    print_separator()
    print()

    # offsets relative to master 
    print("Clock Offsets\n", flush=True)
    clock_differences = {"Master": 0.0}
    print(f"Master       : {0:+.2f} sec", flush=True)
    for client_name, record in client_records.items():
        difference = record["time"] - master_start
        clock_differences[client_name] = difference
        print(f"{client_name:<13}: {difference:+.2f} sec", flush=True)

    
    accepted = dict(clock_differences)
    rejected = {}
    if FILTER_ENABLED:
        for client_name, difference in list(accepted.items()):
            if client_name != "Master" and abs(difference) > MAX_OFFSET:
                rejected[client_name] = accepted.pop(client_name)
        if rejected:
            print(
                f"\n[Outlier filter ENABLED] Excluding nodes beyond "
                f"+/-{MAX_OFFSET:.0f}s: {list(rejected.keys())}",
                flush=True,
            )
               

    mean_difference = sum(accepted.values()) / len(accepted)
    print(f"\nAverage Offset: {mean_difference:+.2f} sec", flush=True)

    print()
    print_separator()
    print()

    # corrections
    print("Corrections\n", flush=True)
    adjustments = {}
    master_adjustment = mean_difference - clock_differences["Master"]
    adjustments["Master"] = master_adjustment
    print(f"Master       : {master_adjustment:+.2f} sec", flush=True)

    for client_name, difference in clock_differences.items():
        if client_name == "Master":
            continue
        if client_name in rejected:
            print(f"{client_name:<13}: EXCLUDED (no correction sent)", flush=True)
            continue
        correction = mean_difference - difference
        adjustments[client_name] = correction
        print(f"{client_name:<13}: {correction:+.2f} sec", flush=True)

    print()
    print_separator()
    print()

    # apply corrections
    current_offset += master_adjustment
    for client_name, record in client_records.items():
        if client_name in rejected:
            continue
        try:
            communicate(record["host"], record["port"], {"cmd": "CORRECTION", "value": adjustments[client_name]})
        except Exception as error:
            print(f"Failed to send correction to {client_name}: {error}", flush=True)

 
    print("Final Clocks\n", flush=True)
    synchronized = {"Master": get_master_clock()}# after applying correction, the master's new logical clock
    print(f"Master       : {format_time(synchronized['Master'])}", flush=True)

    for client_name, record in client_records.items():
        try:
            response = communicate(record["host"], record["port"], {"cmd": "CLOCK_REQUEST"})
            synchronized[client_name] = response["time"]
            print(f"{client_name:<13}: {format_time(response['time'])}", flush=True)
        except Exception as error:
            print(f"{client_name:<13}: UNREACHABLE ({error})", flush=True)

    print()
    print_separator()
    print()

    final_spread = (max(synchronized.values()) - min(synchronized.values())) * 1000
    print(f"Final synchronization error (max-min spread): {final_spread:.1f} ms", flush=True)


if __name__ == "__main__":
    main()
