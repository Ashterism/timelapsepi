#!/bin/bash
# sandbox/boot_report.sh

LOG="/home/pi/data/statuslogs/boot_report_$(date +%Y%m%d_%H%M%S).log"

{
  echo "📦 Boot Report @ $(date)"
  echo "------------------------------"

  echo "🔌 Power Source (PiJuice):"
  pijuice_cli get powerinput

  echo -e "\n🔋 Battery:"
  pijuice_cli get battery

  echo -e "\n📶 Wi-Fi:"
  iwconfig wlan0 | grep -i power
  nmcli device show wlan0 | grep -i STATE

  echo -e "\n🛡️ SSH:"
  systemctl is-active ssh && systemctl status ssh | head -n 10

  echo -e "\n🕘 Uptime:"
  uptime

  echo -e "\n📡 IP Address:"
  ip a | grep inet

  echo -e "\n📓 Last 20 SSH log lines:"
  journalctl -u ssh --no-pager | tail -20

} >> "$LOG" 2>&1