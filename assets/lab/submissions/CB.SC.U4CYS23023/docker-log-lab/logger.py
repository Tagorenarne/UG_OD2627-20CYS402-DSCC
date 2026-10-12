import time
import datetime
import os

os.makedirs("/data", exist_ok=True)

log_path = "/data/logs.txt"

while True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"Log entry at: {timestamp}\n")
    print(f"Written log entry at: {timestamp}")
    time.sleep(5)