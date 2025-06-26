#!/bin/bash

source /home/ash/timelapse/config.env
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
