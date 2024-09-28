#!/bin/bash
# was still going to fail, because no display was connected, if you still see it here, it's either it works or the issue that affects browser start not to wait for browser long enough is still present
/app/executables/browsers/chrome/chrome --no-sandbox &
sleep 5
pkill chrome

python -u run.py