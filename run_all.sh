#!/bin/bash -e

echo "[INFO] Starting run_all at $(date)"

# Wake Wi-Fi
sudo /sbin/ifconfig wlan0 up
sleep 5

# Always log status, even if no Wi-Fi
/usr/bin/python3 /home/ash/timelapse/log_status.py

# Try to connect to the internet
ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[WARN] No internet. Attempting reconnect..."
  sudo systemctl restart dhcpcd
  sleep 10
  ping -c 1 -W 5 8.8.8.8 > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "[ERROR] Still no internet. Skipping upload."
  else
    echo "[INFO] Wi-Fi reconnected. Uploading..."
    /usr/bin/python3 /home/ash/timelapse/upload_status.py
  fi
else
  echo "[INFO] Internet OK. Uploading..."
  /usr/bin/python3 /home/ash/timelapse/upload_status.py
fi

# Optional: disable Wi-Fi if not SSH'd in
if ! who | grep "pts/" > /dev/null; then
  echo "[INFO] No SSH session. Disabling Wi-Fi."
  sudo /sbin/ifconfig wlan0 down
fi

echo "[INFO] Script complete at $(date)"
