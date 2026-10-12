import os
import mysql.connector

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

print("Database Details")
print("----------------")
print("Host:", host)
print("Port:", port)
print("User:", user)
print("Database:", database)

try:
    conn = mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database
    )

    if conn.is_connected():
        print("\nConnected Successfully!")

        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()

        print("Current Database:", result[0])

        cursor.close()
        conn.close()

except Exception as e:
    print("\nConnection Failed")
    print(e)