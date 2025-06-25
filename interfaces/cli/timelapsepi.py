#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from dotenv import dotenv_values, set_key
import sys
from pathlib import Path

# Append correct absolute path to functions/
sys.path.append(str(Path(__file__).resolve().parents[2] / "timelapse/functions"))

from log_util import log

BASE_PATH = Path("/home/ash/timelapse")
CONFIG_PATH = BASE_PATH / "operations/config.env"
SESSIONS_PATH = BASE_PATH / "sessions"
PHOTO_SCRIPT = BASE_PATH / "functions/photo.sh"
START_SCRIPT = BASE_PATH / "functions/start_timelapse.py"
STATUS_SCRIPT = BASE_PATH / "functions/status_timelapse.py"
STOP_SCRIPT = BASE_PATH / "functions/stop_timelapse.py"

config = dotenv_values(CONFIG_PATH)
WIFI_MODES = ["client", "hotspot", "none"]

def print_menu():
    print("\n📋 timelapsepi: Status + Control")
    print("────────────────────────────────────")
    for key, val in config.items():
        if key == "WIFI_MODE":
            print(f"[→] WIFI_MODE: {val}")
        else:
            print(f"[{'✓' if val == 'true' else '✗'}] {key}")
    print("\nCommands:")
    print("  start     → begin new timelapse")
    print("  stop      → stop active session")
    print("  status    → view session status")
    print("  test      → take test photo")
    print("  wifi      → cycle Wi-Fi mode")
    print("  toggle X  → toggle a config.env flag (e.g. LOGGING_ENABLED)")
    print("  refresh   → reload config.env")
    print("  exit      → quit CLI\n")

def run_start():
    subprocess.run(["python3", str(START_SCRIPT)])

def run_status():
    sessions = sorted(SESSIONS_PATH.iterdir(), key=os.path.getmtime, reverse=True)
    for session in sessions:
        config_file = session / "timelapse_config.json"
        if config_file.exists():
            subprocess.run(["python3", str(STATUS_SCRIPT), str(config_file)])
            return
    print("⚠️ No session config found.")

def run_stop():
    sessions = sorted(SESSIONS_PATH.iterdir(), key=os.path.getmtime, reverse=True)
    for session in sessions:
        pid_file = session / "runner.pid"
        if pid_file.exists():
            subprocess.run(["python3", str(STOP_SCRIPT), str(session)])
            return
    print("⚠️ No running session found.")

def run_test_photo():
    subprocess.run(["bash", str(PHOTO_SCRIPT)])

def toggle_flag(flag):
    if flag not in config:
        print("Unknown setting.")
        return
    if config[flag] == "true":
        new_val = "false"
    else:
        new_val = "true"
    set_key(CONFIG_PATH, flag, new_val)
    print(f"Toggled {flag} → {new_val}")
    log(f"Toggled {flag} → {new_val}", "timelapsepi.log")

def cycle_wifi_mode():
    current = config.get("WIFI_MODE", "none")
    idx = WIFI_MODES.index(current) if current in WIFI_MODES else -1
    next_mode = WIFI_MODES[(idx + 1) % len(WIFI_MODES)]
    set_key(CONFIG_PATH, "WIFI_MODE", next_mode)
    print(f"Cycled WIFI_MODE → {next_mode}")
    log(f"Cycled WIFI_MODE → {next_mode}", "timelapsepi.log")

def main():
    print_menu()
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "exit":
            break
        elif cmd == "start":
            run_start()
        elif cmd == "stop":
            run_stop()
        elif cmd == "status":
            run_status()
        elif cmd == "test":
            run_test_photo()
        elif cmd == "wifi":
            cycle_wifi_mode()
        elif cmd.startswith("toggle "):
            flag = cmd.split(" ", 1)[1].strip().upper()
            toggle_flag(flag)
        elif cmd == "refresh":
            global config
            config = dotenv_values(CONFIG_PATH)
            print_menu()
        else:
            print("❓ Unknown command.")
            print_menu()

if __name__ == "__main__":
    main()
