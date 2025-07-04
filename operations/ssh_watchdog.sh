#!/bin/bash

LOG_FILE="/home/ash/timelapse/data/logs/sshd_watchdog.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo "$TIMESTAMP - 📡 IP address: $IP_ADDRESS" >> "$LOG_FILE"

STATUS=$(systemctl is-active ssh)
PORT_LISTENING=$(ss -tuln | grep ':22 ')

if [[ "$STATUS" == "active" && -n "$PORT_LISTENING" ]]; then
    echo "$TIMESTAMP - ✅ SSHD is active and port 22 is listening." >> "$LOG_FILE"
else
    echo "$TIMESTAMP - ⚠️ SSHD issue detected. Restarting..." >> "$LOG_FILE"
    systemctl restart ssh
    sleep 2
    STATUS_AFTER=$(systemctl is-active ssh)
    PORT_LISTENING_AFTER=$(ss -tuln | grep ':22 ')

    if [[ "$STATUS_AFTER" == "active" && -n "$PORT_LISTENING_AFTER" ]]; then
        echo "$TIMESTAMP - 🔁 Restart successful. SSHD is now active and reachable." >> "$LOG_FILE"
    else
        echo "$TIMESTAMP - ❗ Restart failed. SSHD may still be unreachable." >> "$LOG_FILE"
    fi
fi
