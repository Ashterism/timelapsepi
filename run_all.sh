#!/bin/bash

# --- Check Wi-Fi ---
ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Wi-Fi down. Restarting dhcpcd..."
  sudo systemctl restart dhcpcd
  sleep 10  # Give it a moment to come back
else
  echo "Wi-Fi OK."
fi


cd /home/ash/timelapse

# Update from GitHub
/usr/bin/git pull origin main

# Log battery + power status
/usr/bin/python3 log_status.py

# Upload to Firebase
/usr/bin/python3 upload_status.py
