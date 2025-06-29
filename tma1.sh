#!/bin/bash
# --- Source relevant files ---
source "$HOME/timelapse/config/config_paths.sh"
echo "LOGGING_SH: $LOGGING_SH" # TEMP DEBUG LINE
source "$LOGGING_SH"
source "$MODE_CONTROL_SH"
run_mode_control # sets values in following sources

source "$CONFIG_FILE"
source "$NETWORK_SH"
source "$DATA_SYNC_SH"
source "$WEBSERVER_SH"

 # --- Script Execution Starts Here ---
 # --- Always start logs first ---
log_start
log_status

# --- Control connectivity ---

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

# --- Script Execution ENDS Here ---