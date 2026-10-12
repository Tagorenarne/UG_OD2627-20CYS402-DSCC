import os, socket, time
from datetime import datetime

SERVER_HOST = os.environ.get("MASTER_HOST", "clock-master")
SERVER_PORT = int(os.environ.get("MASTER_PORT", 5000))
NODE_NAME = os.environ.get("CLIENT_ID", "client")
TIME_OFFSET = float(os.environ.get("CLOCK_OFFSET", 0))  
SYNC_DELAY = float(os.environ.get("SYNC_INTERVAL", 10))
CONTINUOUS = os.environ.get("REPEAT", "true").lower() == "true"

def get_client_time():
    return time.time() + TIME_OFFSET     

def get_actual_time():
    return time.time()                    

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

def synchronize():
    starting_clock = get_client_time()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(10)
    connection.connect((SERVER_HOST, SERVER_PORT))

    send_time = get_client_time() # client's clock time before sending the request
    connection.sendall(b"TIME_REQUEST")
    response_data = connection.recv(1024).decode()
    receive_time = get_client_time() # client's time immediately after reciving the response
    connection.close()

    server_time = float(response_data.split("=")[1])
    round_trip = receive_time - send_time #round-trip time
    network_delay = round_trip / 2 #delay - half of rtt
    adjusted_time = server_time + network_delay
    clock_error = adjusted_time - get_actual_time()

    print("========== CRISTIAN'S ALGORITHM ==========", flush=True)
    print(f"Client ID       : {NODE_NAME}", flush=True)
    print(f"Initial Clock   : {format_time(starting_clock)}\n", flush=True)
    print(f"T1              : {format_time(send_time)}", flush=True)
    print(f"Master Time     : {format_time(server_time)}", flush=True)
    print(f"T2              : {format_time(receive_time)}\n", flush=True)
    print(f"RTT             : {round_trip*1000:.1f} ms", flush=True)
    print(f"Estimated Delay : {network_delay*1000:.1f} ms\n", flush=True)
    print(f"Corrected Clock : {format_time(adjusted_time)}", flush=True)
    print(f"Final Error     : {clock_error*1000:.1f} ms", flush=True)
    print("============================================\n", flush=True)

def main():
    time.sleep(3)  
    if CONTINUOUS:
        while True:
            try:
                synchronize()
            except Exception as error:
                print(f"[{NODE_NAME}] Sync failed: {error}", flush=True)
            time.sleep(SYNC_DELAY)
    else:
        synchronize()

if __name__ == "__main__":
    main()
