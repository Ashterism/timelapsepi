#!/bin/bash

LOG_FILE="/home/ash/timelapse/data/logs/sshd_watchdog.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
IP=$(hostname -I | awk '{print $1}')  # Get the first IP

# Check port 22 using netcat (nc)
if nc -z -w 2 "$IP" 22; then
    echo "$TIMESTAMP - ✅ SSH port 22 reachable on $IP." >> "$LOG_FILE"
else
    echo "$TIMESTAMP - ❌ SSH port 22 unreachable on $IP. Restarting SSH..." >> "$LOG_FILE"
    systemctl restart ssh
    sleep 2
    if nc -z -w 2 "$IP" 22; then
        echo "$TIMESTAMP - 🔁 Restart fixed port 22." >> "$LOG_FILE"
    else
        echo "$TIMESTAMP - ❗ Restart failed. Port 22 still unreachable." >> "$LOG_FILE"
    fi
fi