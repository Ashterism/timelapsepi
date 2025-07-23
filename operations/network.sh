# Function: check for ssh connection
is_ssh_session() {
  local WHO_OUT
  WHO_OUT=$(who)
  log "[DEBUG] who output: $WHO_OUT"
  echo "$WHO_OUT" | grep -qE "\(.*\)"  # Matches sessions with a remote IP (actual SSH)
}
 
 # Function: bring_up_wifi()
bring_up_wifi() {
  if is_ssh_session; then
    log "[INFO] SSH session detected - skipping wlan0 up"
    return
  fi
  log "[INFO] Wi-Fi mode: client - bringing up wlan0"
  sudo systemctl stop hostapd
  sudo systemctl disable hostapd
  sudo systemctl enable wpa_supplicant

  sudo ip link set wlan0 down
  sudo ip addr flush dev wlan0
  sudo ip link set wlan0 up
  sudo systemctl start wpa_supplicant
  if ! timeout 30s sudo /sbin/ifconfig wlan0 up; then
    log "[ERROR] wlan0 up timed out at $(date)"
  fi
  ip a show wlan0 | grep -q "inet " || log "[WARN] wlan0 has no IP"
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
    sudo /sbin/ifconfig wlan0 down
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

  log "[INFO] Starting hotspot mode..."
  sudo systemctl stop wpa_supplicant
  sudo systemctl disable wpa_supplicant
  if systemctl is-enabled hostapd &> /dev/null; then
    log "[INFO] hostapd already enabled - skipping enable"
  else
    sudo systemctl enable hostapd
  fi
  if systemctl is-enabled dnsmasq &> /dev/null; then
    log "[INFO] dnsmasq already enabled - skipping enable"
  else
    sudo systemctl enable dnsmasq
  fi

  sudo iw dev wlan0 disconnect 2>/dev/null || true
  sudo ip link set wlan0 down
  sudo ip addr flush dev wlan0
  sudo ip addr add 192.168.4.1/24 dev wlan0
  sudo ip link set wlan0 up
  sudo systemctl start dnsmasq
  sudo systemctl start hostapd
}

disable_hotspot() {
  log "[INFO] Stopping hotspot mode..."
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq
  sudo ip link set wlan0 down
  sudo ip addr flush dev wlan0
}