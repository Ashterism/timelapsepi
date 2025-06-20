#!/bin/bash 

LOG_PATH="/home/ash/timelapse/_local/run.log"
cd /home/ash/timelapse

echo "$(date): run_all triggered" >> "$LOG_PATH"
echo "[INFO] Starting run_all at $(date)"

# Log power + battery
# Do this first to ensure always happens
if ! timeout 20s /usr/bin/python3 log_status.py; then
  echo "[ERROR] log_status.py timed out at $(date)" >> "$LOG_PATH"
fi

# Wake Wi-Fi
if ! timeout 30s sudo /sbin/ifconfig wlan0 up; then
  echo "[ERROR] wlan0 up timed out at $(date)" >> "$LOG_PATH"
fi
sleep 5

# Check for internet
if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
  echo "[INFO] Internet OK. Updating from GitHub..."
  if ! timeout 20s /usr/bin/git pull origin main; then
    echo "[ERROR] git pull failed at $(date)" >> "$LOG_PATH"
  fi
else
  echo "[WARN] No internet. Trying reconnect..."
  if ! timeout 15s sudo /sbin/ifconfig wlan0 down && sudo /sbin/ifconfig wlan0 up; then
    echo "[ERROR] Wi-Fi reset failed at $(date)" >> "$LOG_PATH"
  fi
  sleep 10
  if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
    echo "[INFO] Reconnected. Updating from GitHub..."
    timeout 20s /usr/bin/git pull origin main || echo "[ERROR] git pull still failed." >> "$LOG_PATH"
  else
    echo "[ERROR] Still no internet. Skipping GitHub pull + Firebase upload." >> "$LOG_PATH"
  fi
fi

# Upload only if internet is available
if ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1; then
  echo "[INFO] Uploading to Firebase..."
  if ! timeout 20s /usr/bin/python3 upload_status.py; then
    echo "[ERROR] upload_status.py failed at $(date)" >> "$LOG_PATH"
  fi
else
  echo "[INFO] Skipped upload due to no internet at $(date)" >> "$LOG_PATH"
fi

# Disable Wi-Fi if not SSH'd in
if ! who | grep "pts/" > /dev/null; then
  echo "[INFO] No SSH session. Disabling Wi-Fi."
  timeout 20s sudo /sbin/ifconfig wlan0 down || echo "[ERROR] wlan0 down failed at $(date)" >> "$LOG_PATH"
fi

echo "$(date): run_all finished" >> "$LOG_PATH"
echo "[INFO] Script complete at $(date)"
