#!/bin/bash

# run these 2 lines once from pi terminal
# nmcli dev wifi connect "SSID" password "yourpassword"
# nmcli con modify hotspot wifi-sec.psk "yourHotspotPassword"

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
    nmcli con down "$HOTSPOT_NAME" 2>/dev/null
    nmcli con up "$WIFI_NAME"
    ;;
  hotspot)
    log "📡 Switching to hotspot mode ($HOTSPOT_NAME)"
    nmcli con down "$WIFI_NAME" 2>/dev/null
    nmcli con up "$HOTSPOT_NAME"
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