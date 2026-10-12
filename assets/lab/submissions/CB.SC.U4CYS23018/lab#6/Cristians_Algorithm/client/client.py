import socket
from datetime import datetime, timedelta
import time

client = socket.socket()

print("Connecting to server...")

client.connect(("server", 8000))

#time when the request gets sent
T0 = time.time()

#we get the server's received time in response to our request
server_time = client.recv(1024).decode()

#time when response is received
T1 = time.time()

server_time = datetime.fromisoformat(server_time)

#calculating round trip time
rtt = T1 - T0

client_time = server_time + timedelta(seconds=rtt / 2)

print("\nCristian's Algorithm")
print("--------------------")
print("Server Time: ", server_time)
print("Round Trip Time: ", rtt, "seconds")
print("Network Delay: ", rtt / 2, "seconds")
print("Synchronized Client Time: ", client_time)

client.close()
