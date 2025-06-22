#!/bin/bash

source /home/ash/timelapse/config.env
LOG_PATH="/home/ash/timelapse/_local/run.log"
cd /home/ash/timelapse

echo "$(date): run_all triggered" >> "$LOG_PATH"
echo "[INFO] Starting run_all at $(date)" >> "$LOG_PATH"

# Log power + battery
if [ "$LOGGING_ENABLED" == "True" ]; then
  echo "[INFO] Logging enabled - running log_status.py" >> "$LOG_PATH"
  if ! timeout 20s /usr/bin/python3 log_status.py; then
    echo "[ERROR] log_status.py timed out at $(date)" >> "$LOG_PATH"
  fi
else
  echo "[INFO] Logging disabled - skipping log_status.py" >> "$LOG_PATH"
fi

# Handle Wi-Fi mode
if [ "$WIFI_MODE" == "client" ]; then
  echo "[INFO] Wi-Fi mode: client - bringing up wlan0" >> "$LOG_PATH"
  if ! timeout 30s sudo /sbin/ifconfig wlan0 up; then
    echo "[ERROR] wlan0 up timed out at $(date)" >> "$LOG_PATH"
  fi
  sleep 5

  # Check for internet
  ONLINE=false
  if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
    ONLINE=true
    echo "[INFO] Internet OK at $(date)" >> "$LOG_PATH"
  else
    echo "[WARN] No internet. Trying reconnect..." >> "$LOG_PATH"
    if ! timeout 15s sudo /sbin/ifconfig wlan0 down && sudo /sbin/ifconfig wlan0 up; then
      echo "[ERROR] Wi-Fi reset failed at $(date)" >> "$LOG_PATH"
    fi
    sleep 10
    if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
      ONLINE=true
      echo "[INFO] Reconnected. Internet OK at $(date)" >> "$LOG_PATH"
    else
      echo "[ERROR] Still no internet. Skipping GitHub pull + Firebase upload at $(date)" >> "$LOG_PATH"
    fi
  fi

  # GitHub pull
  if [ "$GITHUB_PULL" == "True" ]; then
    if [ "$ONLINE" == "true" ]; then
      echo "[INFO] Pulling latest from GitHub..." >> "$LOG_PATH"
      if ! timeout 20s /usr/bin/git pull origin main; then
        echo "[ERROR] git pull failed at $(date)" >> "$LOG_PATH"
      fi
    else
      echo "[INFO] GitHub sync skipped - no internet" >> "$LOG_PATH"
    fi
  else
    echo "[INFO] GitHub pull disabled by config" >> "$LOG_PATH"
  fi

  # Firebase upload
  if [ "$FIREBASE_UPLOAD" == "True" ]; then
    if [ "$ONLINE" == "true" ]; then
      echo "[INFO] Uploading to Firebase..." >> "$LOG_PATH"
      if ! timeout 20s /usr/bin/python3 upload_status.py; then
        echo "[ERROR] upload_status.py failed at $(date)" >> "$LOG_PATH"
      fi
    else
      echo "[INFO] Firebase upload skipped - no internet" >> "$LOG_PATH"
    fi
  else
    echo "[INFO] Firebase upload disabled by config" >> "$LOG_PATH"
  fi

elif [ "$WIFI_MODE" == "hotspot" ]; then
  echo "[INFO] Wi-Fi mode: hotspot - enabling access point" >> "$LOG_PATH"
  ./scripts/hotspot_mode.sh

else
  echo "[INFO] Wi-Fi mode: none - skipping all network activity" >> "$LOG_PATH"
fi

echo "[INFO] Script complete at $(date)" >> "$LOG_PATH"
echo "$(date): run_all finished" >> "$LOG_PATH"
