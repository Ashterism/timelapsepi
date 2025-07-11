#!/bin/bash

# Source centralised paths
source "$HOME/timelapse/config/config_paths.sh"

# FUNCTION: start webserver
start_webserver() {
  check_webserver
  STATUS=$?
  if [ "$STATUS" -eq 0 ]; then
    # log "[INFO] Webserver already running and responsive - skipping start"
    return
  elif [ "$STATUS" -eq 2 ]; then
    log "[INFO] Webserver not responding - restarting"
    restart_webserver
    return
  elif [ "$STATUS" -eq 1 ]; then
    if [ -f "$ROOT_DIR/data/temp/webserver.pid" ]; then
      log "[INFO] Removing stale PID file"
      rm -f "$ROOT_DIR/data/temp/webserver.pid"
    fi
  fi

  log "[INFO] Starting FastAPI webserver"
  mkdir -p "$ROOT_DIR/data/temp"
  mkdir -p "$ROOT_DIR/data/logs"
  LOG_FILE="$ROOT_DIR/data/logs/webserver.log"
  nohup uvicorn interfaces.web.webserver:app --host 0.0.0.0 --port 5000 > "$LOG_FILE" 2>&1 &
  echo $! > "$ROOT_DIR/data/temp/webserver.pid"
}

# FUNCTION: stop webserver
stop_webserver() {
  if [ -f "$ROOT_DIR/data/temp/webserver.pid" ]; then
    PID=$(cat "$ROOT_DIR/data/temp/webserver.pid")
    if ps -p $PID > /dev/null 2>&1; then
      log "[INFO] Stopping FastAPI webserver (PID $PID)"
      kill "$PID"
    fi
    rm "$ROOT_DIR/data/temp/webserver.pid"
  else
    log "[INFO] No webserver PID found - nothing to stop"
  fi
}

# FUNCTION: restart webserver
restart_webserver() {
  log "[INFO] Restarting FastAPI webserver"
  stop_webserver
  sleep 1  # small delay to ensure clean shutdown
  start_webserver
}

# FUNCTION: hard reset webserver
restart_webserver_hard() {
  if [ -f "$ROOT_DIR/data/temp/webserver.pid" ]; then
    PID=$(cat "$ROOT_DIR/data/temp/webserver.pid")
    log "[INFO] Force killing FastAPI webserver (PID $PID)"
    kill -9 $PID 2>/dev/null || log "[WARN] Failed to kill process $PID"
    rm -f "$ROOT_DIR/data/temp/webserver.pid"
  else
    log "[INFO] No webserver PID found - nothing to force kill"
  fi
}

# FUNCTION: check webserver
check_webserver() {
  if curl -s --max-time 2 http://localhost:5000/health | grep -q OK; then
    log "[INFO] Webserver is running and responsive (detected via port 5000)"
    return 0
  fi

  if [ -f "$ROOT_DIR/data/temp/webserver.pid" ]; then
    PID=$(cat "$ROOT_DIR/data/temp/webserver.pid")
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
# FUNCTION: configure webserver based on config
config_webserver() {
  if [ "$WEBSERVER_ENABLED" == "true" ]; then
    log "[INFO] Config flag enabled - ensuring webserver is running"
    start_webserver
  else
    log "[INFO] Config flag disabled - ensuring webserver is stopped"
    stop_webserver
  fi
}