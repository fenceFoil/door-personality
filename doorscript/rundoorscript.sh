cd /home/pi/door-personality/doorscript
touch doorscript.log
PYTHONHASHSEED=0
python3 -u doorscript.py >> doorscript.log 2>&1 &
