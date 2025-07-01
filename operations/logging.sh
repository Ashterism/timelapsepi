# Set ROOT_DIR if not already set (called from .bashrc)
: "${ROOT_DIR:=$HOME/timelapse}"

# Source centralised paths
source "$ROOT_DIR/config/config_paths.sh"

# Function: log()
log() {
  : "${LOG_PATH:=$LOGS_DIR/run.log}"
  mkdir -p "$(dirname "$LOG_PATH")"
  echo "$1" >> "$LOG_PATH"
}

 # Function: log_start()
log_start() {
  log "$(date): TMA-1 triggered"
  log "[INFO] Starting tma1.sh at $(date)"
}

 # Function: log_end()
log_end() {
  log "[INFO] Script complete at $(date)"
  log "$(date): TMA-1 finished"
}

 # Function: log_status()
log_status() {
  if [ "$LOGGING_ENABLED" == "true" ]; then
    log "[INFO] Logging enabled - running log_status.py"
    if ! timeout 20s /usr/bin/python3 "$ROOT_DIR/operations/log_status.py"; then
      log "[ERROR] log_status.py timed out at $(date)"
    fi
  else
    log "[INFO] Logging disabled - skipping log_status.py"
  fi
}