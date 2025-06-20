#!/usr/bin/env python3

import os
from dotenv import load_dotenv, set_key
from datetime import datetime

LOG_PATH = "/home/ash/timelapse/_local/button_trigger.log"
with open(LOG_PATH, "a") as f:
    f.write(f"{datetime.now()}: toggle_wifi_mode.py triggered\n")

CONFIG_PATH = "/home/ash/config.env"
load_dotenv(CONFIG_PATH)

def get_mode():
    with open(CONFIG_PATH, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("WIFI_CLIENT_MODE"):
            return "client" if "True" in line else "hotspot"
    return "unknown"

def toggle_mode():
    current_mode = get_mode()
    if current_mode == "client":
        set_key(CONFIG_PATH, "WIFI_CLIENT_MODE", "False")
        set_key(CONFIG_PATH, "WIFI_HOTSPOT", "True")
        print("[INFO] Switched to hotspot mode.")
        os.system("/usr/bin/pijuice_cli led blink orange 3")
    elif current_mode == "hotspot":
        set_key(CONFIG_PATH, "WIFI_CLIENT_MODE", "True")
        set_key(CONFIG_PATH, "WIFI_HOTSPOT", "False")
        print("[INFO] Switched to client mode.")
        os.system("/usr/bin/pijuice_cli led blink green 3")
    else:
        print("[ERROR] Unable to determine current mode.")

    # Immediately run main logic to apply config change
    os.system("/home/ash/timelapse/run_all.sh &")

toggle_mode()
