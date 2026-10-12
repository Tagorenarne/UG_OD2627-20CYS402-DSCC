import os
import psycopg2

# Read environment variables
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

print("Database Connector Application")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Database: {database}")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=database
    )
    print("Connected Successfully!")

except Exception as e:
    print("Connection Failed (Expected because dummy values are used)")
    print(e)