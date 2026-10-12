import time
from datetime import datetime
import os

os.makedirs('/app/logs', exist_ok=True)
log_file_path = '/app/logs/time.log'

print("Timestamp logger started... Press Ctrl+C to stop.", flush=True)

while True:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Print to terminal
    print(current_time, flush=True)

    # Save to file
    with open(log_file_path, 'a') as f:
        f.write(f"{current_time}\n")
        f.flush()

    time.sleep(5)
