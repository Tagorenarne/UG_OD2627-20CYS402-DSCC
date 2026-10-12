import socket
import datetime
import os
import time

def start_client():
    cid = os.environ.get('CLIENT_ID', 'Unknown')
    offset_seconds = int(os.environ.get('CLOCK_OFFSET', 0))
    
    # Extract client index number to stagger logs and prevent line scrambling
    try:
        client_idx = int(cid.split('-')[-1])
    except:
        client_idx = 1

    time.sleep(3) # Wait for master to initialize
    
    # Generate initial desynchronized clock
    logical_offset = datetime.timedelta(seconds=offset_seconds)
    initial_time = datetime.datetime.now() + logical_offset
    time_str = initial_time.strftime("%H:%M:%S.%f")
    
    s = socket.socket()
    s.connect(('berkeley-master', 5000))
    
    # Send initial time to master
    s.send(f"{cid}|{time_str}".encode())
    
    # Receive breakdown: MASTER_TIME|AVG_OFFSET|DIFF|CORRECTION
    data = s.recv(1024).decode()
    s.close()
    
    master_time_str, avg_offset_str, diff_str, correction_str = data.split('|')
    avg_offset = float(avg_offset_str)
    diff = float(diff_str)
    correction = float(correction_str)
    
    # Calculate corrected clock
    corrected_time = initial_time + datetime.timedelta(seconds=correction)
    
    # Build complete step-by-step log block
    output_block = (
        f"\n=======================================================\n"
        f"               BERKELEY SYNC: {cid}\n"
        f"=======================================================\n"
        f"[Step 1: Local Clock Initialization]\n"
        f"  • Configured Drift Offset  : {offset_seconds:+} sec\n"
        f"  • Initial Local Clock      : {time_str}\n\n"
        f"[Step 2: Comparison with Master]\n"
        f"  • Master Baseline Time     : {master_time_str}\n"
        f"  • Calculated Difference    : {diff:+.4f} sec ({'Ahead' if diff > 0 else 'Behind'})\n\n"
        f"[Step 3: Network Consensus & Correction]\n"
        f"  • Network Average Offset   : {avg_offset:+.4f} sec\n"
        f"  • Correction Formula       : Correction = Avg_Offset - Difference\n"
        f"  • Step Calculation         : ({avg_offset:+.2f}) - ({diff:+.2f})\n"
        f"  • Target Clock Adjustment  : {correction:+.4f} sec\n\n"
        f"[Step 4: Clock Adjustment Result]\n"
        f"  • Adjusted Clock Value     : {corrected_time.strftime('%H:%M:%S.%f')}\n"
        f"=======================================================\n"
    )
    
    # Stagger printing order: Client-1 prints first, then Client-2, etc.
    time.sleep(client_idx * 0.15)
    print(output_block, flush=True)

if __name__ == '__main__':
    start_client()
