#!/bin/bash

cd /home/ash/timelapse

# Check Wi-Fi before anything else
if ! ping -q -c1 -W1 8.8.8.8 > /dev/null; then
  echo "$(date): No network, restarting wlan0" >> /var/log/wificheck.log
  /sbin/ifdown wlan0 && sleep 5 && /sbin/ifup wlan0
  exit 1  # skip the rest of the script if offline
fi

# Update from GitHub
/usr/bin/git pull origin main

# Log battery + power status
/usr/bin/python3 log_status.py

# Upload to Firebase
/usr/bin/python3 upload_status.py
