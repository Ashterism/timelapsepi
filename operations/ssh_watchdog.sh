#!/bin/bash

# CONFIG
LOG_FILE="/home/ash/timelapse/data/logs/sshd_watchdog.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# LOG IP
echo "$TIMESTAMP - 📡 IP address: $IP_ADDRESS" >> "$LOG_FILE"

# CHECK SSH STATUS
STATUS=$(systemctl is-active ssh)

# CHECK IF PORT 22 IS LISTENING ON THE IP
nc -z "$IP_ADDRESS" 22
NC_STATUS=$?

if [[ "$STATUS" = "active" && "$NC_STATUS" -eq 0 ]]; then
    echo "$TIMESTAMP - ✅ SSHD is active and reachable." >> "$LOG_FILE"
else
    echo "$TIMESTAMP - ⚠️ SSHD issue detected. Restarting..." >> "$LOG_FILE"
    systemctl restart ssh
    sleep 2
    STATUS_AFTER=$(systemctl is-active ssh)
    nc -z "$IP_ADDRESS" 22
    NC_STATUS_AFTER=$?

    if [[ "$STATUS_AFTER" = "active" && "$NC_STATUS_AFTER" -eq 0 ]]; then
        echo "$TIMESTAMP - 🔁 Restart successful. SSHD is now active and reachable." >> "$LOG_FILE"
    else
        echo "$TIMESTAMP - ❗ Restart failed. SSHD may still be unreachable." >> "$LOG_FILE"
    fi
fi