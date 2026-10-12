import json
import os
import time
from datetime import datetime, timezone
from urllib.request import urlopen


def synchronize(master_time, rtt, client_time):
    corrected = master_time + rtt / 2
    return corrected, corrected - client_time


def clock_text(value):
    return datetime.fromtimestamp(value, timezone.utc).strftime("%H:%M:%S.%f")[:-3]


def main():
    client_id = os.getenv("CLIENT_ID", "client1")
    initial_offset = float(os.getenv("CLOCK_OFFSET", "-8"))
    master = os.getenv("MASTER_URL", "http://master:5000")
    delays = [float(value) for value in os.getenv("DELAYS_MS", "0,100,200,500").split(",")]
    for experiment, delay in enumerate(delays, 1):
        # Reset to the configured offset for an independent experiment.
        offset = initial_offset
        t1 = time.time() + offset
        start = time.monotonic()
        with urlopen(f"{master}/time?delay_ms={delay}", timeout=15) as response:
            result = json.load(response)
        finish = time.monotonic()
        wall_at_receive = time.time()
        t2 = wall_at_receive + offset
        rtt = finish - start
        corrected, correction = synchronize(result["master_time"], rtt, t2)
        offset += correction
        # Containers share a host clock. This reference is only for evaluation.
        reference = wall_at_receive + result["master_offset"]
        row = {
            "experiment": experiment, "client": client_id, "delay_ms": delay,
            "initial_offset_s": initial_offset, "t1": t1,
            "master_time": result["master_time"], "t2": t2,
            "rtt_ms": rtt * 1000, "estimated_delay_ms": rtt * 500,
            "correction_s": correction, "corrected_clock": corrected,
            "final_offset_s": offset, "error_ms": (corrected - reference) * 1000,
        }
        print(f"\nCRISTIAN: {client_id}, experiment {experiment}, delay {delay:g} ms")
        print(f"Initial Clock   : {clock_text(t1)} (offset {initial_offset:+g}s)")
        print(f"T1              : {clock_text(t1)}")
        print(f"Master Time     : {clock_text(result['master_time'])}")
        print(f"T2              : {clock_text(t2)}")
        print(f"RTT             : {rtt * 1000:.3f} ms")
        print(f"Estimated Delay : {rtt * 500:.3f} ms")
        print(f"Corrected Clock : {clock_text(corrected)}")
        print(f"Final Error     : {row['error_ms']:+.3f} ms")
        print("RESULT " + json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
