#!/bin/bash

set -e

service postgresql start

until pg_isready -h 127.0.0.1 -U postgres >/dev/null 2>&1
do
    sleep 1
done

if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='midterm_user'" | grep -q 1
then
    runuser -u postgres -- psql -c "CREATE USER midterm_user WITH PASSWORD 'midterm_pass';"
fi

if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='midterm_db'" | grep -q 1
then
    runuser -u postgres -- createdb -O midterm_user midterm_db
fi

runuser -u postgres -- psql -c "ALTER USER midterm_user WITH PASSWORD 'midterm_pass';"

runuser -u postgres -- psql -d midterm_db -f /midterm-exam/database/init.sql

exec python /midterm-exam/web/app.py
