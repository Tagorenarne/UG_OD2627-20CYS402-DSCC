import socket
import datetime
import os
import time

def format_time(dt):
    return dt.strftime("%H:%M:%S.%f")[:-3]

def start_client():
    client_id = os.environ.get('CLIENT_ID', 'Unknown-Client')
    offset_seconds = int(os.environ.get('CLOCK_OFFSET', 0))
    master_host = 'clock-master'
    master_port = 5000

    # Brief sleep to ensure master container starts first
    time.sleep(2)

    # Initial Logical Clock
    logical_offset = datetime.timedelta(seconds=offset_seconds)
    initial_clock = datetime.datetime.now() + logical_offset

    s = socket.socket()
    
    # Step 1: Record T1
    t1 = datetime.datetime.now() + logical_offset
    
    # Step 2: Send Request
    s.connect((master_host, master_port))
    
    # Step 3: Receive Master Time
    master_time_str = s.recv(1024).decode()
    master_time = datetime.datetime.strptime(master_time_str, "%Y-%m-%d %H:%M:%S.%f")
    
    # Step 4: Record T2
    t2 = datetime.datetime.now() + logical_offset
    s.close()

    # Step 5: Calculate RTT
    rtt = (t2 - t1).total_seconds()
    rtt_ms = rtt * 1000

    # Step 6: Estimate Delay
    estimated_delay_ms = rtt_ms / 2
    estimated_delay_td = datetime.timedelta(milliseconds=estimated_delay_ms)

    # Step 7: Calculate Corrected Time
    corrected_clock = master_time + estimated_delay_td
    
    # Calculate Final Error (difference between corrected clock and actual system time)
    # Since master represents absolute truth (system time), error is Corrected - System Time
    true_system_time = datetime.datetime.now()
    final_error_ms = abs((corrected_clock - true_system_time).total_seconds()) * 1000

    print("========== CRISTIAN'S ALGORITHM ==========\n")
    print(f"Client ID       : {client_id}")
    print(f"Initial Clock   : {format_time(initial_clock)}\n")
    print(f"T1              : {format_time(t1)}")
    print(f"Master Time     : {format_time(master_time)}")
    print(f"T2              : {format_time(t2)}\n")
    print(f"RTT             : {rtt_ms:.0f} ms")
    print(f"Estimated Delay : {estimated_delay_ms:.0f} ms\n")
    print(f"Corrected Clock : {format_time(corrected_clock)}")
    print(f"Final Error     : {final_error_ms:.0f} ms\n")

if __name__ == '__main__':
    start_client()
