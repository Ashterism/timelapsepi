#!/bin/bash

start_webserver() {
  log "[INFO] Starting Flask webserver"
  nohup python3 /home/ash/timelapse/web/webserver.py > /dev/null 2>&1 &
  echo $! > /home/ash/timelapse/_local/webserver.pid
}

stop_webserver() {
  if [ -f /home/ash/timelapse/_local/webserver.pid ]; then
    PID=$(cat /home/ash/timelapse/_local/webserver.pid)
    if ps -p $PID > /dev/null 2>&1; then
      log "[INFO] Stopping Flask webserver (PID $PID)"
      kill $PID
    fi
    rm /home/ash/timelapse/_local/webserver.pid
  else
    log "[INFO] No webserver PID found - nothing to stop"
  fi
}