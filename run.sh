#!/bin/bash
cleanup() {
  rm -f /tmp/.X*-lock
}
trap cleanup EXIT


Xvfb ${DISPLAY} -screen 0 ${RESOLUTION} & 

x11vnc -display ${DISPLAY} -forever -nopw -listen 0.0.0.0 &

sleep 3

setup.sh

python -u run.py