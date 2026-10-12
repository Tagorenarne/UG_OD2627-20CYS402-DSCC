#!/bin/bash

# start database
if [ ! -d "/var/lib/mysql/mysql" ]; then
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql > /dev/null
fi

mysqld_safe --datadir=/var/lib/mysql &

# wait for database to start
until mysqladmin ping --silent 2>/dev/null; do
    sleep 1
done

# create database and tables
mysql < /midterm-exam/database/init.sql

# start web app
python /midterm-exam/web/app.py
