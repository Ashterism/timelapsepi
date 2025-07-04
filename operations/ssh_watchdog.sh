#!/bin/bash

# CONFIG
LOG_FILE="/home/ash/timelapse/data/logs/sshd_watchdog.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# CHECK SSHD STATUS
STATUS=$(systemctl is-active ssh)

# ACT BASED ON STATUS
if [ "$STATUS" = "active" ]; then
    echo "$TIMESTAMP - ✅ SSHD is active." >> "$LOG_FILE"
else
    echo "$TIMESTAMP - ❌ SSHD is NOT active. Attempting restart..." >> "$LOG_FILE"
    systemctl restart ssh
    sleep 2
    STATUS_AFTER=$(systemctl is-active ssh)
    if [ "$STATUS_AFTER" = "active" ]; then
        echo "$TIMESTAMP - 🔁 Restart successful. SSHD is now active." >> "$LOG_FILE"
    else
        echo "$TIMESTAMP - ❗ Restart failed. SSHD still not active." >> "$LOG_FILE"
    fi
fi
