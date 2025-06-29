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
   bring_up_wifi       # Only runs if NOT in an SSH session
  check_internet       # Will try to recover if no internet, unless SSH
  pull_git             # Only if configured to do so
  upload_firebase      # Only if configured to do so
  maybe_drop_wifi      # Will drop Wi-Fi unless SSH or DROP_WIFI_AFTER=false
  config_webserver     # Handles webserver state according to config
fi

elif [ "$WIFI_MODE" == "hotspot" ]; then
  log "[INFO] Wi-Fi mode: hotspot - enabling access point"
  enable_hotspot

elif [ "$WIFI_MODE" == "none" ]; then
  log "[INFO] Wi-Fi mode: none - no connectivity mode active (silent logging only)"

else
  log "[WARN] Unknown Wi-Fi mode: $WIFI_MODE - skipping all network activity"
fi

log_end

# --- Script Execution ENDS Here ---