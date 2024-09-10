#!/bin/bash

# Function to clean up lock files
cleanup() {
  rm -f /tmp/.X*-lock
}

# Trap EXIT signal to run cleanup function
trap cleanup EXIT

# Check if resolution is passed as argument, otherwise use default
RESOLUTION=${1:-1920x1080x24}

# Start Xvfb with the specified or default resolution
Xvfb ${DISPLAY} -screen 0 ${RESOLUTION} > /dev/null 2>&1 & 

# Start x11vnc with the specified display
x11vnc -display ${DISPLAY} -forever -nopw -listen 0.0.0.0 > /dev/null 2>&1 &
