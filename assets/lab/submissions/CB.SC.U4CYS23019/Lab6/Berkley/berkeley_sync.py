#!/usr/bin/env python3
"""
Berkeley Clock Synchronization Algorithm
Standalone multi-threaded simulation representing distributed nodes.
"""

import time
import threading
from datetime import datetime

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]

class Node:
    def __init__(self, node_id, clock_offset, is_master=False):
        self.node_id = node_id
        self.clock_offset = clock_offset
        self.is_master = is_master
        self.initial_offset = clock_offset
        self.history = []

    def get_time(self):
        """Returns local logical clock time."""
        return time.time() + self.clock_offset

    def adjust_clock(self, adjustment):
        """Adjusts local clock by the calculated offset."""
        before = self.get_time()
        self.clock_offset += adjustment
        after = self.get_time()
        return before, after

def berkeley_sync_round(master, slaves, network_latency=0.01):
    """
    Executes one round of the Berkeley Clock Synchronization Algorithm.
    """
    print("\n" + "=" * 76)
    print("                 BERKELEY CLOCK SYNCHRONIZATION ALGORITHM")
    print("=" * 76)
    print(f"Master Node : {master.node_id} (Initial Offset: {master.initial_offset:+.3f}s)")
    print(f"Slaves      : {len(slaves)} nodes")
    print("-" * 76)

    # 1. Master polls all slaves
    slave_records = []
    
    for slave in slaves:
        # T1: Master time before request
        t1 = master.get_time()
        
        # Simulate network delay to slave
        time.sleep(network_latency)
        
        # Slave reads its local clock
        t_slave = slave.get_time()
        
        # Simulate return trip delay
        time.sleep(network_latency)
        
        # T2: Master time when reply is received
        t2 = master.get_time()
        
        # RTT and estimated one-way delay
        rtt = t2 - t1
        delay = rtt / 2.0
        
        # Estimated time of slave at instant T2
        t_slave_est = t_slave + delay
        
        # Offset relative to master at instant T2
        # (positive means slave is ahead of master, negative means slave is behind)
        offset = t_slave_est - t2
        
        slave_records.append({
            "slave": slave,
            "t1": t1,
            "t_slave": t_slave,
            "t2": t2,
            "rtt": rtt,
            "delay": delay,
            "offset": offset
        })

    # 2. Master considers all offsets (including its own offset = 0.0)
    all_offsets = [0.0] + [rec["offset"] for rec in slave_records]
    
    # Calculate average offset
    avg_offset = sum(all_offsets) / len(all_offsets)

    # 3. Calculate adjustments
    master_adj = avg_offset - 0.0
    for rec in slave_records:
        rec["adj"] = avg_offset - rec["offset"]

    # 4. Print Summary Table
    print(f"{'Node':<12} {'Initial Clock':<16} {'RTT (ms)':<10} {'Offset (s)':<12} {'Adjustment (s)':<14} {'Sync Clock':<16}")
    print("-" * 76)

    # Master adjustment
    m_before, m_after = master.adjust_clock(master_adj)
    print(f"{master.node_id:<12} {format_time(m_before):<16} {'-':<10} {'+0.000':<12} {master_adj:+14.4f} {format_time(m_after):<16}")

    # Slaves adjustments
    for rec in slave_records:
        s = rec["slave"]
        s_before, s_after = s.adjust_clock(rec["adj"])
        print(f"{s.node_id:<12} {format_time(s_before):<16} {round(rec['rtt']*1000, 2):<10.2f} {rec['offset']:+12.4f} {rec['adj']:+14.4f} {format_time(s_after):<16}")

    print("-" * 76)
    print(f"Average System Offset Adjustment : {avg_offset:+.4f} s")
    print("=" * 76 + "\n")

if __name__ == "__main__":
    # Create master with 0s offset
    master = Node("Master", clock_offset=0.0, is_master=True)

    # Create 4 slaves with varying offsets matching standard lab setup
    slaves = [
        Node("Slave-1", clock_offset=-8.0),
        Node("Slave-2", clock_offset=+6.0),
        Node("Slave-3", clock_offset=-4.0),
        Node("Slave-4", clock_offset=+10.0),
    ]

    berkeley_sync_round(master, slaves, network_latency=0.02)
