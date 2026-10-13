import time
from datetime import datetime
import os

os.makedirs("/app/logs", exist_ok=True)

print("Logger started...")

while True:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]

    with open("/app/logs/time.log", "a") as file:
        file.write(timestamp + "\n")

    time.sleep(5)