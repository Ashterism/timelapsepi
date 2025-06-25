#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values, set_key

# Allow importing from project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config_paths import (
    CONFIG_PATH, SESSIONS_PATH, PHOTO_SCRIPT,
    START_SCRIPT, STATUS_SCRIPT, STOP_SCRIPT
)

# Also allow log_util import
sys.path.append(str(Path(__file__).resolve().parents[2] / "timelapse/functions"))
from log_util import log

config = dotenv_values(CONFIG_PATH)
WIFI_MODES = ["client", "hotspot", "none"]

def cli_log(msg):
    log(msg, "timelapsepi.log")

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
    print("  clear     → clear the screen")
    print("  exit      → quit CLI\n")

def run_start():
    try:
        subprocess.run(["python3", str(START_SCRIPT)])
        run_status()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        cli_log(f"Failed to start: {e}")

def run_status():
    SESSIONS_PATH.mkdir(parents=True, exist_ok=True)
    try:
        sessions = sorted(SESSIONS_PATH.iterdir(), key=os.path.getmtime, reverse=True)
        for session in sessions:
            config_file = session / "timelapse_config.json"
            if config_file.exists():
                subprocess.run(["python3", str(STATUS_SCRIPT), str(config_file)])
                return
        print("⚠️ No session config found.")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        cli_log(f"Status check failed: {e}")

def run_stop():
    SESSIONS_PATH.mkdir(parents=True, exist_ok=True)
    try:
        sessions = sorted(SESSIONS_PATH.iterdir(), key=os.path.getmtime, reverse=True)
        for session in sessions:
            pid_file = session / "runner.pid"
            if pid_file.exists():
                subprocess.run(["python3", str(STOP_SCRIPT), str(session)])
                return
        print("⚠️ No running session found.")
    except Exception as e:
        print(f"❌ Error stopping session: {e}")
        cli_log(f"Stop failed: {e}")

def run_test_photo():
    if not PHOTO_SCRIPT.exists():
        print("❌ photo.sh not found!")
        cli_log("Test photo failed — script missing")
        return
    subprocess.run(["bash", str(PHOTO_SCRIPT)])

def toggle_flag(flag):
    if flag not in config:
        print("Unknown setting.")
        return
    new_val = "false" if config[flag] == "true" else "true"
    set_key(CONFIG_PATH, flag, new_val)
    print(f"Toggled {flag} → {new_val}")
    cli_log(f"Toggled {flag} → {new_val}")

def cycle_wifi_mode():
    current = config.get("WIFI_MODE", "none")
    idx = WIFI_MODES.index(current) if current in WIFI_MODES else -1
    next_mode = WIFI_MODES[(idx + 1) % len(WIFI_MODES)]
    set_key(CONFIG_PATH, "WIFI_MODE", next_mode)
    print(f"Cycled WIFI_MODE → {next_mode}")
    cli_log(f"Cycled WIFI_MODE → {next_mode}")

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
        elif cmd == "clear":
            os.system("clear")
        else:
            print("❓ Unknown command.")
            print_menu()

if __name__ == "__main__":
    main()
