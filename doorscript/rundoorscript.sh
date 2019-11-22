#!/bin/sh
cd /home/pi/door-personality/doorscript
touch doorscript.log
python3 -u doorscript.py >> doorscript.log 2>&1 &
