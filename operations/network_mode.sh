#!/bin/bash

CONFIG_FILE="$(dirname "$0")/network_mode.conf"
LOG_TAG="[network_mode]"

log() {
  echo "$LOG_TAG $1"
}

# Check config file
if [[ ! -f "$CONFIG_FILE" ]]; then
  log "❌ Config file not found: $CONFIG_FILE"
  exit 1
fi

# Load profile names
source "$CONFIG_FILE"

if [[ -z "$HOTSPOT_NAME" || -z "$WIFI_NAME" ]]; then
  log "❌ Config missing HOTSPOT_NAME or WIFI_NAME"
  exit 1
fi

MODE="$1"
if [[ -z "$MODE" ]]; then
  log "❌ No mode specified. Use: wifi, hotspot, or off"
  exit 1
fi

case "$MODE" in
  wifi)
    log "🔁 Switching to Wi-Fi client mode ($WIFI_NAME)"

    # Stop manual hotspot services
    systemctl stop hostapd
    systemctl stop dnsmasq

    # Remove manual IP config on wlan0
    ip addr flush dev wlan0

    # Re-enable NetworkManager control on wlan0
    nmcli dev set wlan0 managed yes

    # Restart NetworkManager so it re-scans wlan0
    systemctl restart NetworkManager

    # Activate Wi-Fi connection
    nmcli con up "$WIFI_NAME"
    ;;

  hotspot)
    log "📡 Switching to hotspot mode ($HOTSPOT_NAME)"

    # Stop Wi-Fi client connection
    nmcli con down "$WIFI_NAME" 2>/dev/null

    # Disable NetworkManager control on wlan0
    nmcli dev set wlan0 managed no

    # Assign static IP for hotspot
    ip addr add 192.168.4.1/24 dev wlan0
    ip link set wlan0 up

    # Start manual hotspot services
    systemctl start hostapd
    systemctl start dnsmasq
    ;;

  off)
    log "📴 Disabling all wireless interfaces"
    nmcli radio wifi off
    ;;
  *)
    log "❌ Invalid mode: $MODE"
    exit 1
    ;;
esac