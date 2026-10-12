#!/bin/bash
# Entrypoint for the Midterm Web Authentication container.
# Initializes MariaDB from database/init.sql, then hands off to Apache in the foreground.

set -e

echo "[entrypoint] starting MariaDB..."
service mariadb start

# Wait for the server to accept connections.
for i in $(seq 1 30); do
    if mariadb-admin ping --silent; then
        echo "[entrypoint] MariaDB is up."
        break
    fi
    sleep 1
done

if [ -f /midterm-exam/database/init.sql ]; then
    echo "[entrypoint] applying database/init.sql..."
    mariadb < /midterm-exam/database/init.sql
    echo "[entrypoint] database initialized."
fi

echo "[entrypoint] starting Apache..."
exec apache2ctl -D FOREGROUND