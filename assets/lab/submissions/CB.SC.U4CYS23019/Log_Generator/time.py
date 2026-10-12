from datetime import datetime
import time
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

log_file = "data/time.log"

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print to console
    print(current_time, flush=True)

    # Save to log file
    with open(log_file, "a") as f:
        f.write(current_time + "\n")

    time.sleep(1)