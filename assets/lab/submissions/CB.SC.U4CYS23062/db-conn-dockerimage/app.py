import os
import mysql.connector

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

print("===================================")
print(" Database Connector Application")
print("===================================")

print(f"Host      : {db_host}")
print(f"Port      : {db_port}")
print(f"Username  : {db_user}")
print(f"Database  : {db_name}")

print("\nAttempting to connect to the database...\n")

try:
    connection = mysql.connector.connect(
        host=db_host,
        port=int(db_port),
        user=db_user,
        password=db_password,
        database=db_name
    )

    if connection.is_connected():
        print("Database connection successful!")
        connection.close()

except Exception as e:
    print("Database connection failed.")
    print("Reason:", e)