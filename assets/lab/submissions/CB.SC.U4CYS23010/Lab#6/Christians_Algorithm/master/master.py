import socket
import datetime
import time
import os

def start_master():
    host = '0.0.0.0'
    port = 5000
    delay_ms = int(os.environ.get('ARTIFICIAL_DELAY_MS', 0))
    ''' can be changed accordinngly on the experiments 1 2 3 4, experiment 1 isi 0 2 is 100 3 is 200 and 4 is 500'''

    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    print(f"Master Time Server running on port {port} with {delay_ms}ms artificial delay...")

    while True:
        conn, addr = s.accept()
        print(f"Received TIME_REQUEST from {addr}")

        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
            
        master_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        conn.send(master_time.encode())
        conn.close()

if __name__ == '__main__':
    start_master()
