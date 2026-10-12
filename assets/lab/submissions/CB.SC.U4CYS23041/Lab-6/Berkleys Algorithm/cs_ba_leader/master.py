#!/usr/bin/env python3
"""
master.py - Berkeley Clock Synchronization :: MASTER / COORDINATOR
=====================================================================
20CYS402 - Distributed Systems and Cloud Computing
Lab #6B - Berkeley Clock Synchronization Algorithm

The master is the *coordinator*.  It is NOT an authoritative time server -
it has no privileged hardware clock.  It simply asks every participant for
its clock, works out everyone's offset, computes the mean offset, and tells
each node how much to add or subtract.  All clocks then agree.

One round of Berkeley:
    1. Master records its own clock                       (M)
    2. Master sends CLOCK_REQUEST to every client         (parallel)
    3. Each client replies with its own clock             (C_i)
    4. offset_i = C_i - M          (master's offset = 0)
    5. average  = (0 + sum(offset_i)) / (n + 1)          (master included)
    6. correction_i = average - offset_i
    7. Master sends CLOCK_SET to each client, applies its own
    8. Every clock now reads  M + average

Environment variables
---------------------
    CLIENTS              comma separated host[:port] list of followers
    CLIENT_PORT          default TCP port for every follower        (5000)
    NODE_ID              label for this node                       (master)
    CLOCK_OFFSET         this node's own initial drift in seconds   (0)
    CLOCK_BASE           logical start time, 'HH:MM:SS' or 'auto'  (12:00:00)
    CLOCK_MODE           'frozen' (lock-step demo) | 'running'     (frozen)
    CLOCK_TICK           seconds added per round in frozen mode     (0.5)
    ROUNDS               how many synchronisation rounds to run     (1)
    ROUND_INTERVAL       seconds between rounds                    (15)
    POLL_MODE            'parallel' or 'sequential'                 (parallel)
    POLL_TIMEOUT         per-follower socket timeout in seconds     (5)
    RTT_COMPENSATION     1 = compensate half the RTT, 0 = raw       (1)
    OUTLIER_THRESHOLD    |offset| above this many sec = faulty; 0=off (0)
    OUTLIER_ACTION       'skip' (do not correct) | 'include'         (skip)
    KEEP_ALIVE           1 = stay running and re-sync periodically   (0)
    IDLE_SLEEP           seconds between refreshes when KEEP_ALIVE=1 (20)
    PRE_SYNC_DELAY       grace delay before the very first poll      (2)
"""

import os
import signal
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from clock import (
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    LogicalClock,
    fmt_clock,
    fmt_signed,
    rpc,
    split_node_spec,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def env(name, default):
    value = os.environ.get(name)
    return default if value is None or value == "" else value


def env_int(name, default):
    try:
        return int(env(name, default))
    except (TypeError, ValueError):
        return default


def env_float(name, default):
    try:
        return float(env(name, default))
    except (TypeError, ValueError):
        return default


def env_bool(name, default):
    return str(env(name, "1" if default else "0")).strip().lower() in (
        "1", "true", "yes", "on",
    )


NODE_ID = env("NODE_ID", "master")
CLOCK_BASE = env("CLOCK_BASE", "12:00:00")
CLOCK_MODE = env("CLOCK_MODE", "frozen")
CLOCK_TICK = env_float("CLOCK_TICK", 0.5)
CLOCK_OFFSET = env_float("CLOCK_OFFSET", 0.0)
CLIENT_PORT = env_int("CLIENT_PORT", DEFAULT_PORT)
POLL_TIMEOUT = env_float("POLL_TIMEOUT", DEFAULT_TIMEOUT)
POLL_MODE = str(env("POLL_MODE", "parallel")).lower()
RTT_COMPENSATION = env_bool("RTT_COMPENSATION", True)
ROUNDS = env_int("ROUNDS", 1)
ROUND_INTERVAL = env_float("ROUND_INTERVAL", 15.0)
OUTLIER_THRESHOLD = env_float("OUTLIER_THRESHOLD", 0.0)
OUTLIER_ACTION = str(env("OUTLIER_ACTION", "skip")).lower()
KEEP_ALIVE = env_bool("KEEP_ALIVE", False)
IDLE_SLEEP = env_float("IDLE_SLEEP", 20.0)
PRE_SYNC_DELAY = env_float("PRE_SYNC_DELAY", 2.0)

OUTLIER_ON = OUTLIER_THRESHOLD > 0 and OUTLIER_ACTION == "skip"


def load_clients():
    """CLIENTS=client1,client2:5000,client3  ->  [('client1',5000), ...]"""
    raw = env("CLIENTS", "client1,client2,client3,client4")
    nodes = []
    for chunk in str(raw).split(","):
        parsed = split_node_spec(chunk, CLIENT_PORT)
        if parsed:
            nodes.append(parsed)
    return nodes


CLIENTS = load_clients()
MASTER_CLOCK = LogicalClock(
    offset=CLOCK_OFFSET,
    base_time=CLOCK_BASE,
    mode=CLOCK_MODE,
    tick=CLOCK_TICK,
)

# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

LINE = "=" * 70
THIN = "-" * 70


def banner(title):
    print(LINE, flush=True)
    print(f"  {title}", flush=True)
    print(LINE, flush=True)


def section(title):
    print(THIN, flush=True)
    print(f"  {title}", flush=True)
    print(THIN, flush=True)


def row(label, value):
    print(f"  {label:<18}: {value}", flush=True)


# ---------------------------------------------------------------------------
# Berkeley steps
# ---------------------------------------------------------------------------


def poll_one(host, port, round_no):
    """
    Steps 2-3: CLOCK_REQUEST / CLOCK_RESPONSE for a single follower.

    Returns a measurement dict, or an error dict if the follower is down.
    """
    record = {
        "node": host, "port": port, "reachable": False,
        "clock": None, "rtt": None, "offset": None,
        "outlier": False, "error": None,
    }
    try:
        leader_clock = MASTER_CLOCK.now()
        t_send = time.monotonic()
        reply = rpc(
            host, port,
            {"cmd": "CLOCK_REQUEST", "round": round_no, "leader_clock": leader_clock},
            timeout=POLL_TIMEOUT,
        )
        t_recv = time.monotonic()

        if reply.get("cmd") != "CLOCK_RESPONSE":
            raise ValueError(f"unexpected reply {reply.get('cmd')!r}")

        record["reachable"] = True
        record["clock"] = float(reply["clock"])
        record["rtt"] = t_recv - t_send
        record["leader_clock"] = leader_clock
        record["pid"] = reply.get("pid")
    except (OSError, TimeoutError, ConnectionError, ValueError, KeyError) as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def poll_all(round_no):
    """Steps 2-3: poll every follower (parallel by default)."""
    if POLL_MODE == "sequential" or len(CLIENTS) == 1:
        return [poll_one(h, p, round_no) for h, p in CLIENTS]
    with ThreadPoolExecutor(max_workers=max(1, len(CLIENTS))) as pool:
        futures = [pool.submit(poll_one, h, p, round_no) for h, p in CLIENTS]
        return [f.result() for f in futures]


def compute_offsets(measurements):
    """
    Step 4: offset of every node relative to the master.

        offset_i = clock_i - master_clock      (the master's own offset is 0)

    A positive offset means the node's clock runs *ahead* of the master.
    With RTT compensation the client's clock is rolled back by half the
    round-trip delay first, so the sample lines up with the instant the
    master sampled its own clock.
    """
    for record in measurements:
        if not record["reachable"]:
            record["offset"] = None
            continue
        client_clock = record["clock"]
        if RTT_COMPENSATION and record["rtt"]:
            # One-way delay is assumed to be RTT/2, so the clock value we
            # received is 'ahead' of the client's clock at the instant the
            # master sampled its own clock.  Back it out to line the two
            # samples up on the same instant.
            client_clock -= record["rtt"] / 2.0
        record["offset"] = clean(client_clock - record["leader_clock"], 3)
    return measurements


def flag_outliers(measurements):
    """
    OPTIONAL ENHANGEMENT - not part of classic Berkeley.

    When OUTLIER_THRESHOLD > 0 a node whose |offset| exceeds the threshold is
    treated as faulty.  OUTLIER_ACTION decides what happens next:
        'skip'    - drop it from the mean and send it no correction
        'include' - keep it in the mean (i.e. detection without exclusion)
    """
    for record in measurements:
        record["outlier"] = bool(
            record["reachable"]
            and OUTLIER_THRESHOLD > 0
            and abs(record["offset"]) > OUTLIER_THRESHOLD
        )
    return measurements


def clean(value, decimals=3):
    """Round a value and collapse negative zero, so tables never show '-0.0'."""
    value = round(float(value), decimals)
    return 0.0 if value == 0 else value


def average_offset(used):
    """
    Step 5: mean offset over the master plus every *used* follower.

        average = (0 + sum(offset_i)) / (n + 1)
    """
    if not used:
        return 0.0
    return clean((0.0 + sum(r["offset"] for r in used)) / (len(used) + 1))


def send_correction(host, port, round_no, correction, target_clock):
    """Step 7: push the correction to one follower."""
    try:
        reply = rpc(
            host, port,
            {"cmd": "CLOCK_SET", "round": round_no,
             "correction": correction, "target_clock": target_clock},
            timeout=POLL_TIMEOUT,
        )
        return reply.get("cmd") == "CLOCK_ACK", reply
    except (OSError, TimeoutError, ConnectionError, ValueError) as exc:
        return False, {"error": f"{type(exc).__name__}: {exc}"}


def verify_one(host, port, round_no):
    """Read a follower's clock back after correction (for the error column)."""
    try:
        reply = rpc(host, port, {"cmd": "CLOCK_VERIFY", "round": round_no},
                    timeout=POLL_TIMEOUT)
        if reply.get("cmd") == "CLOCK_VERIFY_RESPONSE":
            return float(reply["clock"]), None
        return None, f"unexpected reply {reply.get('cmd')!r}"
    except (OSError, TimeoutError, ConnectionError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# One full Berkeley round
# ---------------------------------------------------------------------------


def sync_round(round_no):
    results = {"round": round_no, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    banner(f"BERKELEY SYNCHRONIZATION  -  ROUND {round_no}   ({results['timestamp']})")

    # ---- Step 1: master clock ------------------------------------------------
    MASTER_CLOCK.set_ticks(round_no)          # frozen mode: advance in lock-step
    master_before = MASTER_CLOCK.now()
    row("Master clock", fmt_clock(master_before))
    row("Polling", f"{len(CLIENTS)} follower(s) in '{POLL_MODE}' mode")

    # ---- Steps 2-3: CLOCK_REQUEST -> CLOCK_RESPONSE -------------------------
    section("Step 1  |  Master sends CLOCK_REQUEST to every node")
    measurements = flag_outliers(compute_offsets(poll_all(round_no)))
    time.sleep(0.15)  # make the request/reply exchange visible in the log

    # ---- Step 4: offsets -----------------------------------------------------
    section("Step 2  |  Clock offsets relative to the master")
    print(f"  {'Node':<12} {'Initial clock':>15} {'Offset':>10} {'RTT':>9} {'Status'}")
    print(f"  {NODE_ID:<12} {fmt_clock(master_before):>15} {fmt_signed(0.0):>10} "
          f"{'-':>9} {'coordinator'}")
    for record in measurements:
        name = record["node"]
        if not record["reachable"]:
            print(f"  {name:<12} {'UNREACHABLE':>15} {'n/a':>10} {'n/a':>9} "
                  f"!! no reply")
        else:
            status = "faulty" if record["outlier"] else "ok"
            print(f"  {name:<12} {fmt_clock(record['clock']):>15} "
                  f"{fmt_signed(record['offset']):>10} "
                  f"{record['rtt'] * 1000:6.1f}ms {status}")

    missing = [r["node"] for r in measurements if not r["reachable"]]
    if missing:
        print(f"\n  !! no reply from: {', '.join(missing)} - "
              f"excluded from this round, the others still synchronise")

    # ---- Outlier detection (optional enhancement) ----------------------------
    if OUTLIER_THRESHOLD > 0:
        faults = [r["node"] for r in measurements if r["outlier"]]
        print(f"\n  Outlier detection ENABLED (threshold +/-{OUTLIER_THRESHOLD:g}s, "
              f"action='{OUTLIER_ACTION}')")
        if OUTLIER_ACTION == "include":
            print("  note: 'include' reports faults but still averages them in")
        if faults:
            print(f"  !! faulty node(s): {', '.join(faults)}")
        else:
            print("  no node exceeded the threshold")

    # ---- Step 5: average offset ---------------------------------------------
    section("Step 3  |  Average offset (master included in the mean)")
    used = [r for r in measurements
            if r["reachable"] and not (OUTLIER_ON and r["outlier"])]
    excluded = [r["node"] for r in measurements
                if r["reachable"] and OUTLIER_ON and r["outlier"]]
    average = clean(average_offset(used))
    terms = " ".join(fmt_signed(r["offset"], 1) for r in used) or "-"
    print(f"  (master=0  {terms})  /  {len(used) + 1}")
    row("Average offset", f"{fmt_signed(average)} sec")
    row("Target time", fmt_clock(master_before + average))
    if excluded:
        print(f"  (removed from the mean: {', '.join(excluded)})")

    # ---- Step 6: corrections -------------------------------------------------
    section("Step 4  |  Corrections  =  average offset - node offset")
    corrections = {NODE_ID: average}
    for record in measurements:
        if record in used:
            corrections[record["node"]] = average - record["offset"]
        else:
            corrections[record["node"]] = None      # unreachable or faulty
    # An unreachable node and a *detected* faulty node are different things,
    # so report each for what it is.
    unreachable_names = {r["node"] for r in measurements if not r["reachable"]}
    for name, value in corrections.items():
        if value is not None:
            shown = f"{fmt_signed(value)} sec"
        elif name in unreachable_names:
            shown = "not applied (node unreachable)"
        else:
            shown = "not applied (faulty node excluded)"
        print(f"  {name:<12}: {shown}")

    # ---- Step 7: apply -------------------------------------------------------
    section("Step 5  |  Applying corrections")
    applied = {}
    for record in used:
        correction = corrections[record["node"]]
        ok, reply = send_correction(
            record["node"], record["port"], round_no,
            correction, master_before + average,
        )
        applied[record["node"]] = float(reply["clock"]) if ok else None
        if ok:
            print(f"  {record['node']:<12}: {fmt_signed(correction)} sec applied "
                  f"-> {fmt_clock(reply['clock'])}")
        else:
            print(f"  {record['node']:<12}: correction FAILED "
                  f"({reply.get('error')})")

    master_correction = corrections[NODE_ID]
    MASTER_CLOCK.apply_correction(master_correction)
    master_after = MASTER_CLOCK.now()
    print(f"  {NODE_ID:<12}: {fmt_signed(master_correction)} sec applied "
          f"-> {fmt_clock(master_after)}")

    # ---- Step 8: final clocks + error ---------------------------------------
    time.sleep(0.3)
    finals = []
    for record in used:
        value, err = verify_one(record["node"], record["port"], round_no)
        finals.append({"node": record["node"], "clock": value, "error": err})

    section("Step 6  |  Final clocks and synchronisation error")
    print(f"  {'Node':<12} {'Final clock':>15} {'Error vs master':>16}")
    print(f"  {NODE_ID:<12} {fmt_clock(master_after):>15} {'0.00 s':>16}")
    for entry in finals:
        if entry["clock"] is None:
            print(f"  {entry['node']:<12} {'n/a':>15} {entry['error'] or 'n/a':>16}")
        else:
            # Error = how far this node is from the master's post-correction clock.
            err = entry["clock"] - master_after
            print(f"  {entry['node']:<12} {fmt_clock(entry['clock']):>15} "
                  f"{fmt_signed(err, 2) + ' s':>16}")

    good = [e["clock"] for e in finals if e["clock"] is not None]
    spread = (max(good) - min(good)) if len(good) > 1 else 0.0
    row("Max spread", f"{spread * 1000:.1f} ms  (largest - smallest final clock)")

    results.update({
        "master_before": master_before,
        "master_after": master_after,
        "master_correction": master_correction,
        "average": average,
        "measurements": measurements,
        "corrections": corrections,
        "applied": applied,
        "finals": finals,
        "excluded": excluded,
        "spread": spread,
    })
    return results


# ---------------------------------------------------------------------------
# Results table (Part L of the hand-out)
# ---------------------------------------------------------------------------


def print_results_table(all_rounds):
    banner("RESULTS TABLE  (for Part L of the lab report)")
    print("| Experiment | Node | Initial Clock | Offset | Average Offset | "
          "Correction | Final Clock | Error |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")

    for result in all_rounds:
        exp = f"Round {result['round']}"
        average = result["average"]
        master_after = result["master_after"]

        print(f"| {exp} | {NODE_ID} | {fmt_clock(result['master_before'])} | "
              f"{fmt_signed(0.0)} | {fmt_signed(average)} | "
              f"{fmt_signed(result['master_correction'])} | "
              f"{fmt_clock(master_after)} | 0.000 |")

        for record in result["measurements"]:
            name = record["node"]
            if not record["reachable"]:
                print(f"| {exp} | {name} | n/a | n/a | {fmt_signed(average)} | "
                      f"n/a | n/a | unreachable |")
                continue
            correction = result["corrections"].get(name)
            applied = result["applied"].get(name)
            if applied is not None:
                error = f"{applied - master_after:+.3f}"
                corr_txt = fmt_signed(correction)
                final_txt = fmt_clock(applied)
            elif record["outlier"]:
                error, corr_txt, final_txt = "n/a", "excluded (faulty)", "n/a"
            else:
                error, corr_txt, final_txt = "n/a", "n/a", "n/a"
            print(f"| {exp} | {name} | {fmt_clock(record['clock'])} | "
                  f"{fmt_signed(record['offset'])} | {fmt_signed(average)} | "
                  f"{corr_txt} | {final_txt} | {error} |")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

STOP = threading.Event()
SERVER = None


def _handle_signal(signum, _frame):
    print(f"\n[master] signal {signum} received - shutting down", flush=True)
    STOP.set()


def main():
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    banner("BERKELEY CLOCK SYNCHRONIZATION ALGORITHM")
    row("Coordinator", NODE_ID)
    row("Followers", ", ".join(f"{h}:{p}" for h, p in CLIENTS))
    row("Clock mode", f"{CLOCK_MODE}  (base {CLOCK_BASE}, "
                      f"tick {CLOCK_TICK:g}s/round)")
    row("Poll mode", POLL_MODE)
    row("RTT compensation", "on" if RTT_COMPENSATION else "off")
    row("Outlier detection", f"ON  (threshold +/-{OUTLIER_THRESHOLD:g}s, "
                             f"action '{OUTLIER_ACTION}')"
                             if OUTLIER_THRESHOLD > 0 else "off (classic Berkeley)")
    row("Container", f"{socket.gethostname()}  pid={os.getpid()}")

    if PRE_SYNC_DELAY > 0:
        print(f"\n  waiting {PRE_SYNC_DELAY:g}s for the followers to finish booting ...",
              flush=True)
        STOP.wait(PRE_SYNC_DELAY)

    all_rounds = []
    for round_no in range(1, ROUNDS + 1):
        if STOP.is_set():
            break
        all_rounds.append(sync_round(round_no))
        if round_no < ROUNDS and not STOP.is_set():
            print(f"\n  next round in {ROUND_INTERVAL:g}s ...", flush=True)
            STOP.wait(ROUND_INTERVAL)

    print_results_table(all_rounds)

    if not KEEP_ALIVE:
        print("[master] synchronisation complete - exiting", flush=True)
        return 0

    print(f"[master] KEEP_ALIVE=1 - re-synchronising every {IDLE_SLEEP:g}s "
          f"(Ctrl-C to stop)", flush=True)
    while not STOP.is_set():
        STOP.wait(IDLE_SLEEP)
        if STOP.is_set():
            break
        all_rounds.append(sync_round(len(all_rounds) + 1))
    print("[master] stopped", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[master] interrupted")
        sys.exit(0)
