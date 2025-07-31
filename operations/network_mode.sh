#!/bin/bash

CONFIG_FILE="$(dirname "$0")/network_mode.conf"
LOG_TAG="[network_mode]"
DEBUG=true

log() {
  if $DEBUG; then
    echo "$LOG_TAG $1"
  fi
}

backup_file() {
  local file=$1
  if [[ -f "$file" && ! -f "${file}.bak" ]]; then
    cp "$file" "${file}.bak"
    log "Backup created for $file"
  fi
}

set_unmanaged_conf() {
  local unmanaged_conf="/etc/NetworkManager/conf.d/unmanaged.conf"
  backup_file "$unmanaged_conf"

  if [[ "$1" == "no" ]]; then
    # Remove wlan0 from unmanaged-devices line
    if grep -q "unmanaged-devices=interface-name:wlan0" "$unmanaged_conf" 2>/dev/null; then
      sed -i '/unmanaged-devices=interface-name:wlan0/d' "$unmanaged_conf"
      log "Removed wlan0 unmanaged line from $unmanaged_conf"
    fi
  else
    # Add unmanaged-devices line if not present
    if ! grep -q "unmanaged-devices=interface-name:wlan0" "$unmanaged_conf" 2>/dev/null; then
      echo -e "[keyfile]\nunmanaged-devices=interface-name:wlan0" >> "$unmanaged_conf"
      log "Added wlan0 unmanaged line to $unmanaged_conf"
    fi
  fi
}

set_dhcpcd_conf() {
  local dhcpcd_conf="/etc/dhcpcd.conf"
  backup_file "$dhcpcd_conf"

  local start_marker="# BEGIN network_mode static wlan0"
  local end_marker="# END network_mode static wlan0"

  if [[ "$1" == "no" ]]; then
    # Remove static IP block if present
    if grep -q "$start_marker" "$dhcpcd_conf"; then
      sed -i "/$start_marker/,/$end_marker/d" "$dhcpcd_conf"
      log "Removed static IP block from $dhcpcd_conf"
    fi
  else
    # Add static IP block if not present
    if ! grep -q "$start_marker" "$dhcpcd_conf"; then
      cat >> "$dhcpcd_conf" <<EOF

$start_marker
interface wlan0
  static ip_address=192.168.4.1/24
  nohook wpa_supplicant
$end_marker
EOF
      log "Added static IP block to $dhcpcd_conf"
    fi
  fi
}

restart_services() {
  systemctl restart NetworkManager
  log "Restarted NetworkManager"
}

MODE="$1"
if [[ -z "$MODE" ]]; then
  echo "$LOG_TAG ❌ No mode specified. Use: wifi, hotspot, or off"
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "$LOG_TAG ❌ Config file not found: $CONFIG_FILE"
  exit 1
fi

source "$CONFIG_FILE"

if [[ -z "$HOTSPOT_NAME" || -z "$WIFI_NAME" ]]; then
  echo "$LOG_TAG ❌ Config missing HOTSPOT_NAME or WIFI_NAME"
  exit 1
fi

case "$MODE" in
  wifi)
    if nmcli device status | grep -q "wlan0.*connected"; then
    log "[INFO] wlan0 is already connected - skipping bring up"
    exit 0
    fi
    echo "$LOG_TAG 🔁 Switch ing to Wi-Fi client mode ($WIFI_NAME)"
   
    # Stop manual hotspot services
    systemctl stop hostapd
    systemctl stop dnsmasq

    # Remove manual IP config from dhcpcd.conf
    set_dhcpcd_conf no

    # Remove wlan0 unmanaged from NetworkManager
    set_unmanaged_conf no

    # Delay to allow NetworkManager to auto-reconnect automatically once wlan0 is managed again
    sleep 5

    # Optional: Log the connection state of wlan0 after delay
    status=$(nmcli device status | grep wlan0)
    log "wlan0 status after enabling managed mode: $status"

    # Flush manual IP if any
    ip addr flush dev wlan0

    # Restart services to apply changes
    restart_services

    # Only bring up connection if it's not already connected
    if ! nmcli -t -f DEVICE,STATE dev | grep -q "^wlan0:connected"; then
      nmcli con up "$WIFI_NAME"
      if [[ $? -ne 0 ]]; then
        echo "$LOG_TAG ❌ Failed to bring up Wi-Fi connection: $WIFI_NAME"
        exit 1
      fi
    else
      log "wlan0 already connected — skipping nmcli con up"
    fi
    ;;

  hotspot)
    echo "$LOG_TAG 📡 Switching to hotspot mode ($HOTSPOT_NAME)"

    # Deactivate Wi-Fi client connection if active
    nmcli con down "$WIFI_NAME" 2>/dev/null

    # Add wlan0 unmanaged to NetworkManager conf
    set_unmanaged_conf yes

    # Add static IP block to dhcpcd.conf
    set_dhcpcd_conf yes

    # Assign static IP manually
    ip addr add 192.168.4.1/24 dev wlan0
    ip link set wlan0 up

    # Restart services to apply changes
    restart_services

    # Start hotspot services
    systemctl start hostapd
    systemctl start dnsmasq
    ;;

  off)
    echo "$LOG_TAG 📴 Disabling all wireless interfaces"
    nmcli radio wifi off
    ;;

  *)
    echo "$LOG_TAG ❌ Invalid mode: $MODE"
    exit 1
    ;;
esac