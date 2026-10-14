import os
import sys
import time
import psycopg2

# Retry connection to database in case it is still starting up
for attempt in range(10):
    try:
        conn = psycopg2.connect(
            host=os.getenv("host"),
            port=os.getenv("port"),
            user=os.getenv("username"),
            password=os.getenv("password"),
            dbname=os.getenv("name"),
        )
        print("connection established")
        conn.close()
        sys.exit(0)
    except psycopg2.OperationalError as e:
        if attempt == 9:
            print("Failed to connect to database after 10 attempts:")
            print(e)
            sys.exit(1)
        print(f"Database connection attempt {attempt + 1} failed, retrying in 2 seconds...")
        time.sleep(2)
