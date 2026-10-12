import socket
import time
import json

def run_client():
    server_host = "time-server"
    server_port = 8080

    print("[Client] Starting Cristian's Algorithm Client...", flush=True)
    # Give the server a moment to start up completely
    time.sleep(3)

    while True:
        try:
            t0 = time.time()
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_host, server_port))
            
            data = client_socket.recv(1024)
            t1 = time.time()
            client_socket.close()

            response = json.loads(data.decode('utf-8'))
            t_server = response["server_time"]

            rtt = t1 - t0
            synchronized_time = t_server + (rtt / 2)

            print(f"[Client] T0 (sent): {t0:.6f}", flush=True)
            print(f"[Client] T1 (recv): {t1:.6f}", flush=True)
            print(f"[Client] RTT: {rtt:.6f} seconds", flush=True)
            print(f"[Client] Server Time: {t_server:.6f}", flush=True)
            print(f"[Client] Synchronized Clock: {synchronized_time:.6f}\n", flush=True)

        except Exception as e:
            print(f"[Client] Error connecting to server: {e}", flush=True)

        time.sleep(5)

if __name__ == "__main__":
    run_client()