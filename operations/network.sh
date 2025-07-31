# Function: check for ssh connection
is_ssh_session() {
  local WHO_OUT
  WHO_OUT=$(who)
  log "[DEBUG] who output: $WHO_OUT"
  echo "$WHO_OUT" | grep -qE "\(.*\)"  # Matches sessions with a remote IP (actual SSH)
}
 
 # Function: bring_up_wifi()
bring_up_wifi() {

  log "[INFO] Switching to Wi-Fi client mode via network_mode.sh"
  sudo ./operations/network_mode.sh wifi
  # Removed manual ifconfig wlan0 up as NetworkManager manages it
  ip a show wlan0 | grep -q "inet " || log "[WARN] wlan0 has no IP"
  sleep 5       
}

 # Function: check_internet()
 # used to check whether to run git/firebase etc syncs
check_internet() {
  ONLINE=false
  if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
    ONLINE=true
    log "[INFO] Internet OK at $(date)"
  else
    log "[WARN] No internet. Trying reconnect..."
    if is_ssh_session; then
      log "[INFO] SSH session detected - skipping Wi-Fi reset"
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
  if is_ssh_session; then
    log "[INFO] SSH session detected - skipping wlan0 down"
    return
  fi

  if [ "$DROP_WIFI_AFTER" == "true" ]; then
    log "[INFO] Dropping wlan0 after tasks"
    sudo ./operations/network_mode.sh off  
  fi
}

# HOTSPOT MANAGEMENT

is_hotspot_active() {
  systemctl is-active hostapd &> /dev/null
}

enable_hotspot() {
 if is_hotspot_active; then
    log "[INFO] Hotspot already active - skipping setup"
    return
  fi
  log "[INFO] Starting hotspot mode via network_mode.sh"
  sudo ./operations/network_mode.sh hotspot
}
