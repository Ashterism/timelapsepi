#!/bin/bash

source /home/ash/timelapse/config/config_paths.sh

CONFIG_PATH="/home/ash/timelapse/config.env"
PRESET_LOADER="/home/ash/timelapse/config/load_preset.sh"

if [ -f "$MODE_CONTROL_FILE" ]; then
  source "$MODE_CONTROL_FILE"
  log "[INFO] Mode control set to: $MODE_CONTROL"
  log "[INFO] Active preset: $ACTIVE_PRESET"
else
  echo "[ERROR] mode_control.env not found!"
  exit 1
fi

if [ "$MODE_CONTROL" == "system" ]; then
  log "[INFO] SYSTEM mode enabled — reloading preset: $ACTIVE_PRESET"
  bash "$PRESET_LOADER" "$ACTIVE_PRESET"
else
  log "[INFO] USER mode — preserving existing config.env"
fi

source "$CONFIG_PATH"
source /home/ash/timelapse/operations/logging.sh
source /home/ash/timelapse/operations/network.sh
source /home/ash/timelapse/operations/data_sync.sh
source /home/ash/timelapse/interfaces/webserver.sh

LOG_PATH="/home/ash/timelapse/data/logs/run.log"
if ! cd /home/ash/timelapse; then
  log "[ERROR] Failed to cd into /home/ash/timelapse"
fi


 # --- Script Execution Starts Here ---
log_start
log_status

if [ "$WIFI_MODE" == "client" ]; then
  bring_up_wifi     # ops # unless ssh active
  check_internet    # ops # 
  pull_git          # ops # if set to do so
  upload_firebase   # ops # if set to do so
  maybe_drop_wifi   # ops # unless ssh active

elif [ "$WIFI_MODE" == "hotspot" ]; then
  log "[INFO] Wi-Fi mode: hotspot - enabling access point"
  enable_hotspot

elif [ "$WIFI_MODE" == "none" ]; then
  log "[INFO] Wi-Fi mode: none - no connectivity mode active (silent logging only)"

else
  log "[WARN] Unknown Wi-Fi mode: $WIFI_MODE - skipping all network activity"
fi

# if [ "$WEBSERVER_ENABLED" == "true" ]; then
#   start_webserver
# else
#   stop_webserver
# fi

log_end
