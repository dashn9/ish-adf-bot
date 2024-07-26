#!/bin/bash
cleanup() {
  rm -f /tmp/.X*-lock
}
trap cleanup EXIT


Xvfb ${DISPLAY} -screen 0 ${RESOLUTION} > /dev/null 2>&1 & 

x11vnc -display ${DISPLAY} -forever -nopw -listen 0.0.0.0 > /dev/null 2>&1 &

sleep 3

./setup.sh

python -u run.py