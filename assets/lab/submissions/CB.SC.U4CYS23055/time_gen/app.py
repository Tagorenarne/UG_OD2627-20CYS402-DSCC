import time
while True:
    with open("log.txt", "a") as f:
        f.write(f"{time.ctime()}: Running\n")
    time.sleep(5)