import os, socket, time
from datetime import datetime

MASTER_HOST = os.environ.get("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.environ.get("MASTER_PORT", 5000))
CLIENT_ID = os.environ.get("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", 0))  
SYNC_INTERVAL = float(os.environ.get("SYNC_INTERVAL", 10))
REPEAT = os.environ.get("REPEAT", "true").lower() == "true"

def client_time():
    return time.time() + CLOCK_OFFSET     

def true_time():
    return time.time()                    

def fmt(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]

def sync_once():
    initial_clock = client_time()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((MASTER_HOST, MASTER_PORT))

    T1 = client_time() # client's clock time before sending the request
    s.sendall(b"TIME_REQUEST")
    data = s.recv(1024).decode()
    T2 = client_time() # client's time immediately after reciving the response
    s.close()

    master_time = float(data.split("=")[1])
    RTT = T2 - T1 #round-trip time
    delay = RTT / 2 #delay - half of rtt
    corrected = master_time + delay
    error = corrected - true_time()

    print("========== CRISTIAN'S ALGORITHM ==========", flush=True)
    print(f"Client ID       : {CLIENT_ID}", flush=True)
    print(f"Initial Clock   : {fmt(initial_clock)}\n", flush=True)
    print(f"T1              : {fmt(T1)}", flush=True)
    print(f"Master Time     : {fmt(master_time)}", flush=True)
    print(f"T2              : {fmt(T2)}\n", flush=True)
    print(f"RTT             : {RTT*1000:.1f} ms", flush=True)
    print(f"Estimated Delay : {delay*1000:.1f} ms\n", flush=True)
    print(f"Corrected Clock : {fmt(corrected)}", flush=True)
    print(f"Final Error     : {error*1000:.1f} ms", flush=True)
    print("============================================\n", flush=True)

def main():
    time.sleep(3)  
    if REPEAT:
        while True:
            try:
                sync_once()
            except Exception as e:
                print(f"[{CLIENT_ID}] Sync failed: {e}", flush=True)
            time.sleep(SYNC_INTERVAL)
    else:
        sync_once()

if __name__ == "__main__":
    main()

