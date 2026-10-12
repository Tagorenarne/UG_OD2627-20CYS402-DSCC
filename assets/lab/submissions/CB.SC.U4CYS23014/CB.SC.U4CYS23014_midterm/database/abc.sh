#!/bin/bash

mysqld_safe --datadir=/var/lib/mysql &

sleep 5

mysql -u root < /midterm-exam/database/init.sql

python /midterm-exam/web/app.py
