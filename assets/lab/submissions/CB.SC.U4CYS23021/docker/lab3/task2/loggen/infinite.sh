#!/bin/sh 

mkdir -p /var/log/dockerexercise
touch /var/log/dockerexercise/data.txt

n=0
while [ $n -lt 100 ]
do
    date >> /var/log/dockerexercise/data.txt
    sleep 1
    n=$((n+1))
done