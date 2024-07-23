#!/bin/bash
cleanup() {
  killall Xvfb
  rm -f /tmp/.X*-lock
}
trap cleanup EXIT

Xvfb :1 -screen 0 1024x768x16 &
sleep 3
python run.py