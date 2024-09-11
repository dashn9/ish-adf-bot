#!/bin/bash

# Function to clean up lock files
cleanup() {
  rm -f /tmp/.X*-lock
}

trap cleanup EXIT
cleanup
pkill -f Xvfb
pkill -f x11vnc
sleep 1

RESOLUTION=${1:-1920x1080x24}

Xvfb -ac ${DISPLAY} -screen 0 ${RESOLUTION} > /dev/null 2>&1 & 

x11vnc -display ${DISPLAY} -forever -nopw -listen 0.0.0.0 > /dev/null 2>&1 &
