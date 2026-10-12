import os
import mysql.connector

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

print(f"Attempting to connect to database '{DB_NAME}' at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")

try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print(f"Connected to database '{DB_NAME}' successfully!")
    conn.close()
except Exception as e:
    print(f"Connection attempt failed: {e}")