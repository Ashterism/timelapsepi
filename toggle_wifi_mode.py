#!/usr/bin/env python3

import os
import subprocess
from dotenv import load_dotenv, set_key
from datetime import datetime
from pijuice import PiJuice
from time import sleep

CONFIG_PATH = "/home/ash/timelapse/config.env"
LOG_PATH = "/home/ash/timelapse/_local/button_trigger.log"

pj = PiJuice(1, 0x14)  # bus 1, address 0x14

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

def flash_led(colour):
    if colour == "orange":
        pj.status.SetLedBlink('D2', 3, [255, 128, 0], 300, [0, 0, 0], 300)
    elif colour == "green":
        pj.status.SetLedBlink('D2', 3, [0, 255, 0], 300, [0, 0, 0], 300)

def switch_to_hotspot():
    log("[INFO] Switching to HOTSPOT mode")
    os.system("sudo ifconfig wlan0 down")
    sleep(1)
    os.system("sudo ifconfig wlan0 up")
    sleep(1)
    os.system("sudo systemctl restart hostapd")
    set_key(CONFIG_PATH, "WIFI_MODE","hotspot")
    flash_led("orange")

def switch_to_client():
    log("[INFO] Switching to CLIENT mode")
    os.system("sudo systemctl stop hostapd")
    os.system("sudo ifconfig wlan0 down")
    sleep(1)
    os.system("sudo ifconfig wlan0 up")
    sleep(1)
    set_key(CONFIG_PATH, "WIFI_MODE", "client")
    flash_led("green")

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