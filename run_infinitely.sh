#!/bin/bash
# Using this script will cause the program to really run infinitely irrespective of any error that might occur, not advisable to use this script
# Change to the directory containing the script
cd "$(dirname "$0")"

while true
do
    python3.10 ./run.py
    if [ $? -ne 0 ]; then
        pkill -f "python3.10 ./run.py"
    fi
    sleep 2
done
