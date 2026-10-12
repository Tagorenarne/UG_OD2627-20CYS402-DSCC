import socket
from datetime import datetime

server = socket.socket()
server.bind(("0.0.0.0", 8000))

#start listening for incoming connections
server.listen(1)

print("Server is listening...")

while True:
    #accepting connection
    connection, address = server.accept()

    print("Client connected: ", address)

    #getting the current server time
    current_time = datetime.now()

    connection.send(str(current_time).encode())
    connection.close()
