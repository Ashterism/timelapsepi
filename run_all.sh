#!/bin/bash

# --- Check Wi-Fi ---
ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[WARN] Wi-Fi down. Reinitialising wlan0 interface..."
  sudo ip link set wlan0 down
  sleep 2
  sudo ip link set wlan0 up
  sleep 10  # Give time to reconnect
else
  echo "[INFO] Wi-Fi OK."
fi

cd /home/ash/timelapse

# Update from GitHub
/usr/bin/git pull origin main

# Log battery + power status
/usr/bin/python3 log_status.py

# Upload to Firebase
/usr/bin/python3 upload_status.py
