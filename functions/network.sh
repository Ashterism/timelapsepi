 # Function: bring_up_wifi()
bring_up_wifi() {
  log "[INFO] Wi-Fi mode: client - bringing up wlan0"
  if ! timeout 30s sudo /sbin/ifconfig wlan0 up; then
    log "[ERROR] wlan0 up timed out at $(date)"
  fi
  sleep 5
}

 # Function: check_internet()
check_internet() {
  ONLINE=false
  if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
    ONLINE=true
    log "[INFO] Internet OK at $(date)"
  else
    log "[WARN] No internet. Trying reconnect..."
    if who | grep -q "pts"; then
      log "[INFO] SSH session detected – skipping Wi-Fi reset"
    else
      if ! timeout 15s sudo /sbin/ifconfig wlan0 down && sudo /sbin/ifconfig wlan0 up; then
        log "[ERROR] Wi-Fi reset failed at $(date)"
      fi
      sleep 10
    fi
    if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
      ONLINE=true
      log "[INFO] Reconnected. Internet OK at $(date)"
    else
      log "[ERROR] Still no internet. Skipping GitHub pull + Firebase upload at $(date)"
    fi
  fi
}

# Function: maybe_drop_wifi()
maybe_drop_wifi() {
  if [ "$DROP_WIFI_AFTER" == "True" ]; then
    if who | grep -q "pts"; then
      log "[INFO] SSH session detected - keeping Wi-Fi on"
    else
      log "[INFO] Dropping Wi-Fi after tasks to conserve power"
      sudo /sbin/ifconfig wlan0 down
    fi
  fi
}