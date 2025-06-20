#!/usr/bin/env python3

import os
from dotenv import dotenv_values, set_key

CONFIG_PATH = "/home/ash/timelapse/config.env"
config = dotenv_values(CONFIG_PATH)

# Order matters here for cycling through modes
WIFI_MODES = ["client", "hotspot", "none"]

def print_menu():
    print("\n📋 timelapsepi: Status and Control")
    print("────────────────────────────────────")
    for key, val in config.items():
        if key == "WIFI_MODE":
            print(f"[→] WIFI_MODE: {val}")
        else:
            print(f"[{'✓' if val == 'True' else '✗'}] {key}")
    print("\nType the name of a setting to toggle it.")
    print("Type 'wifi' to cycle WIFI_MODE.")
    print("Or type 'status' to refresh, or 'exit' to quit.\n")

def toggle(key):
    if key not in config:
        print("Unknown setting.")
        return
    if key == "WIFI_MODE":
        print("Use 'wifi' to change Wi-Fi mode.")
        return
    new_val = "False" if config[key] == "True" else "True"
    set_key(CONFIG_PATH, key, new_val)
    config[key] = new_val
    print(f"Toggled {key} → {new_val}")

def cycle_wifi_mode():
    current = config.get("WIFI_MODE", "none")
    idx = WIFI_MODES.index(current) if current in WIFI_MODES else -1
    next_mode = WIFI_MODES[(idx + 1) % len(WIFI_MODES)]
    set_key(CONFIG_PATH, "WIFI_MODE", next_mode)
    config["WIFI_MODE"] = next_mode
    print(f"Cycled WIFI_MODE → {next_mode}")

print_menu()
while True:
    cmd = input("> ").strip().lower()
    if cmd == "exit":
        break
    elif cmd == "status":
        config = dotenv_values(CONFIG_PATH)  # Reload in case changed externally
        print_menu()
    elif cmd == "wifi":
        cycle_wifi_mode()
    else:
        toggle(cmd)
