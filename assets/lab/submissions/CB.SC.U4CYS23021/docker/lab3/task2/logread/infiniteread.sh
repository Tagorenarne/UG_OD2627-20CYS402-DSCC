#!/bin/sh

while [ ! -f /var/log/dockerexercise/data.txt ]
do
    echo "no logs yet"
    sleep 1
done

n=0
while [ $n -lt 100 ]
do
    tail -n 1 /var/log/dockerexercise/data.txt
    sleep 1
    n=$((n+1))
done