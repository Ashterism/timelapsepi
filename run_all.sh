#!/bin/bash

source /home/ash/timelapse/config.env
source /home/ash/timelapse/functions/logging.sh
source /home/ash/timelapse/functions/network.sh
source /home/ash/timelapse/functions/websync.sh

LOG_PATH="/home/ash/timelapse/_local/run.log"
cd /home/ash/timelapse


 # --- Script Execution Starts Here ---
log_start
log_status

if [ "$WIFI_MODE" == "client" ]; then
  if who | grep -q "pts"; then  # checks for SSH session 
    log "[INFO] SSH session detected - skipping Wi-Fi operations"
  else
    bring_up_wifi
    check_internet
    pull_git
    upload_firebase
    maybe_drop_wifi
  fi

elif [ "$WIFI_MODE" == "hotspot" ]; then
  log "[INFO] Wi-Fi mode: hotspot - enabling access point"
  ./scripts/hotspot_mode.sh

elif [ "$WIFI_MODE" == "none" ]; then
  log "[INFO] Wi-Fi mode: none - no connectivity mode active (silent logging only)"

else
  log "[WARN] Unknown Wi-Fi mode: $WIFI_MODE - skipping all network activity"
fi

log_end
