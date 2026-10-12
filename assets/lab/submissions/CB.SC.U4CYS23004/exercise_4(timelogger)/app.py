import time
from datetime import datetime
import os

os.makedirs('/app/logs', exist_ok=True)
log_file_path = '/app/logs/time.log'

print("Timestamp logger started... Press Ctrl+C to stop.")

while True:
    with open(log_file_path, 'a') as f:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{current_time}\n")
        
        f.flush() 
    time.sleep(5)