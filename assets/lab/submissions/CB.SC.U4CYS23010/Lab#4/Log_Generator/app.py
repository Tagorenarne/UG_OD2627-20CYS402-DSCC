import os
import time
from datetime import datetime

os.makedirs("/data", exist_ok=True)

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Current Time: {current_time}", flush=True)

    with open("/data/log.txt", "a") as file:
        file.write(current_time + "\n")

    time.sleep(5)
