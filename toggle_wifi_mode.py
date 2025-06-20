#!/usr/bin/env python3

import os
import subprocess
from dotenv import load_dotenv, set_key
from datetime import datetime

CONFIG_PATH = "/home/ash/timelapse/config.env"
LOG_PATH = "/home/ash/timelapse/_local/button_trigger.log"

def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {msg}\n")

def get_current_wifi_mode():
    try:
        output = subprocess.check_output(["iw", "dev", "wlan0", "info"]).decode()
        for line in output.splitlines():
            if "type" in line:
                return line.strip().split()[-1]  # managed or AP
    except Exception as e:
        log(f"[ERROR] Failed to detect Wi-Fi mode: {e}")
    return "unknown"

def switch_to_hotspot():
    log("[INFO] Switching to HOTSPOT mode")
    os.system("sudo ifconfig wlan0 down")
    os.system("sleep 1")
    os.system("sudo ifconfig wlan0 up")
    os.system("sleep 1")
    os.system("sudo systemctl restart hostapd")
    set_key(CONFIG_PATH, "WIFI_CLIENT_MODE", "False")
    set_key(CONFIG_PATH, "WIFI_HOTSPOT", "True")
    os.system("/usr/bin/pijuice_cli led blink orange 3")

def switch_to_client():
    log("[INFO] Switching to CLIENT mode")
    os.system("sudo systemctl stop hostapd")
    os.system("sudo ifconfig wlan0 down")
    os.system("sleep 1")
    os.system("sudo ifconfig wlan0 up")
    os.system("sleep 1")
    set_key(CONFIG_PATH, "WIFI_CLIENT_MODE", "True")
    set_key(CONFIG_PATH, "WIFI_HOTSPOT", "False")
    os.system("/usr/bin/pijuice_cli led blink green 3")

def toggle_mode():
    load_dotenv(CONFIG_PATH)
    current = get_current_wifi_mode()
    log(f"[INFO] Current mode detected: {current}")
    if current == "managed":
        switch_to_hotspot()
    elif current == "AP":
        switch_to_client()
    else:
        log("[ERROR] Unknown Wi-Fi mode — no action taken")
        return
    os.system("/home/ash/timelapse/run_all.sh &")

toggle_mode()
