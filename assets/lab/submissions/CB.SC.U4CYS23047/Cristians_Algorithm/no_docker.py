import time

def server_time():
    return time.time()


def client_time():
    start = time.time() #client records time before contacting server
    server = server_time() #retrieves the time from server
    end = time.time() #client records time again after getting response
    rtt = end - start

    corrected_time = server + (rtt / 2)

    return corrected_time, rtt

corrected_time, rtt = client_time()

print("Server Time :", server_time())
print("RTT         :", rtt, "seconds")
print("Client Time :", corrected_time)

#find the skew between the 2 clocks
#Clock skew is the difference between two clocks
#it will be 0 since we're using the same system clock