#!/bin/bash

LOGFILE="/home/ash/timelapse/data/logs/sys_monitor.log"

while true; do
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOGFILE"
  free -h >> "$LOGFILE"
  vmstat 1 5 >> "$LOGFILE"
  ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 15 >> "$LOGFILE"
  echo "" >> "$LOGFILE"
  sleep 60
done