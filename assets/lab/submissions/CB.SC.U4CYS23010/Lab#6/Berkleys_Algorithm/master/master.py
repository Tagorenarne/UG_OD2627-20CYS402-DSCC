import socket
import datetime
import os

def start_master():
    port = 5000
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(5)
    
    num_clients = int(os.environ.get('NUM_CLIENTS', 4))
    connections = []
    
    print(f"Master Time Daemon waiting for {num_clients} clients...\n")
    
    for _ in range(num_clients):
        conn, addr = s.accept()
        data = conn.recv(1024).decode()
        cid, ctime_str = data.split('|')
        ctime = datetime.datetime.strptime(ctime_str, "%H:%M:%S.%f")
        connections.append((conn, cid, ctime))
        
    master_time = datetime.datetime.now()
    master_time_str = master_time.strftime("%H:%M:%S.%f")
    print(f"Master Baseline Time      : {master_time_str}")
    
    diffs = [0.0]
    for conn, cid, ctime in connections:
        ctime = ctime.replace(year=master_time.year, month=master_time.month, day=master_time.day)
        diff = (ctime - master_time).total_seconds()
        diffs.append(diff)
        
    avg_offset = sum(diffs) / len(diffs)
    master_correction = avg_offset - 0.0
    
    print(f"Calculated Average Offset : {avg_offset:+.2f} sec")
    print(f"Master Correction Applied : {master_correction:+.2f} sec\n")
    
    for i, (conn, cid, ctime) in enumerate(connections):
        client_diff = diffs[i+1]
        correction = avg_offset - client_diff
        payload = f"{master_time_str}|{avg_offset:+.4f}|{client_diff:+.4f}|{correction:+.4f}"
        conn.send(payload.encode())
        conn.close()
        
if __name__ == '__main__':
    start_master()
