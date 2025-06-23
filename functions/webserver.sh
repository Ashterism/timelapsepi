#!/bin/bash

# FUNCTION: start webserver
start_webserver() {
  check_webserver
  STATUS=$?
  if [ "$STATUS" -eq 0 ]; then
    log "[INFO] Webserver already running and responsive - skipping start"
    return
  elif [ "$STATUS" -eq 2 ]; then
    log "[INFO] Webserver not responding - restarting"
    restart_webserver
    return
  fi

  log "[INFO] Starting Flask webserver"
  nohup python3 /home/ash/timelapse/web/webserver.py > /dev/null 2>&1 &
  echo $! > /home/ash/timelapse/_local/webserver.pid
}

# FUNCTION: stop webserver
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

# FUNCTION: restart webserver
restart_webserver() {
  log "[INFO] Restarting Flask webserver"
  stop_webserver
  sleep 1  # small delay to ensure clean shutdown
  start_webserver
}

# FUNCTION: check webserver
check_webserver() {
  if curl -s --max-time 2 http://localhost:5000/ > /dev/null; then
    log "[INFO] Webserver is running and responsive (detected via port 5000)"
    return 0
  fi

  if [ -f /home/ash/timelapse/_local/webserver.pid ]; then
    PID=$(cat /home/ash/timelapse/_local/webserver.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
      log "[WARN] Webserver running (PID $PID) but not responding on port 5000"
      return 2
    else
      log "[WARN] PID file found but process $PID is not running"
      return 1
    fi
  else
    log "[INFO] No webserver PID found"
    return 1
  fi
}