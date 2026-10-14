import socket
import time
from datetime import datetime
import json

host = "0.0.0.0"
port = 8888


def show_time(value):
    return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S.%f")


server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((host, port))
server.listen(5)

print("Cristian's Algorithm - Time Server")

print("Server running on port", port)
print("Current Server Time:", show_time(time.time()))


try:

    while True:

        connection, address = server.accept()

        try:
            request = connection.recv(1024)

            if not request:
                connection.close()
                continue

            
            server_time = time.time()
            server_time_text = show_time(server_time)

            print("Request from", address[0], address[1])
            print(
                "Server Time:",
                server_time_text,
                "(",
                round(server_time, 6),
                ")"
            )

            response = {
                "server_time": server_time,
                "server_time_str": server_time_text
            }

            connection.send(json.dumps(response).encode())

            print("Time sent to client")
            print("-" * 50)

        except Exception as error:
            print("Error:", error)

        finally:
            connection.close()

except KeyboardInterrupt:
    print("Server stopped")
  
finally:
    server.close()
