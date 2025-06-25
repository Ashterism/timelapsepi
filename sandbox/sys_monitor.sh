#!/bin/bash

LOGFILE="/home/ash/timelapse/data/logs/sys_monitor.log"

while true; do
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOGFILE"
  free -h >> "$LOGFILE"
  vmstat 1 5 >> "$LOGFILE"
  ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 15 >> "$LOGFILE"
  echo "" >> "$LOGFILE"
  echo "Flask health: $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health)" >> "$LOGFILE"
  df -h / >> "$LOGFILE"
  vcgencmd measure_temp >> "$LOGFILE" 2>/dev/null
  sleep 60
done