#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values, set_key

# Allow importing from project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config.config_paths import (
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

#
# ─────────────────────────────────────────
# Section: Menu Display
# ─────────────────────────────────────────
#
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
    print("  preset    → switch to a predefined mode")
    print("  toggle X  → toggle a config.env flag (e.g. LOGGING_ENABLED)")
    print("  refresh   → reload config.env")
    print("  clear     → clear the screen")
    print("  exit      → quit CLI\n")
    
#
# ─────────────────────────────────────────
# Section: Preset Management
# ─────────────────────────────────────────
#
def change_preset():
    def show_menu():
        print("\n=================================")
        print("PRESETS (see /config/presets.env)")
        print("=================================")
        print("1. MAINS_AND_WIFI")
        print("2. BATTERY_AND_WIFI")
        print("3. BATTERY_AND_HOTSPOT")
        print("4. BATTERY_NO_CXTION")
        print("5. See option descriptions")
    
    while True:
        show_menu()
        choice = input("Select preset [1-4] or 5 for info: ").strip()
        
        if choice == "5":
            print("\n📝 PRESET DESCRIPTIONS")
            print("--------------------------")
            print("# MAINS_AND_WIFI")
            print("    - everything on all of the time")
            print("    - syncs code and logs every 15 minutes\n")
            print("# BATTERY_AND_WIFI")
            print("    - drops wifi between uploads to save power")
            print("    - syncs code and logs every 15 minutes\n")
            print("# BATTERY_AND_HOTSPOT")
            print("    - hotspot on until mode exited")
            print("    - no sync\n")
            print("# BATTERY_NO_CXTION")
            print("    - no wireless connectivity")
            print("    - no sync\n")
            input("Press Enter to return to the menu...")
            continue

        presets = {
            "1": "MAINS_AND_WIFI",
            "2": "BATTERY_AND_WIFI",
            "3": "BATTERY_AND_HOTSPOT",
            "4": "BATTERY_NO_CXTION"
        }
        preset = presets.get(choice)

        if preset:
            result = subprocess.run(["bash", "config/load_preset.sh", preset])
            if result.returncode == 0:
                print(f"✅ Preset '{preset}' applied.")
                cli_log(f"Preset changed to {preset}")
            else:
                print("❌ Failed to apply preset.")
                cli_log(f"Failed to apply preset: {preset}")
            break
        else:
            print("❌ Invalid selection.")
            cli_log(f"Invalid preset selection: {choice}")

#
# ─────────────────────────────────────────
# Section: Timelapse Control Commands
# ─────────────────────────────────────────
#
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
            pid_file = session / "timelapse_runner.pid"
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

#
# ─────────────────────────────────────────
# Section: Config Flag Toggling
# ─────────────────────────────────────────
#
def toggle_flag(flag):
    if flag not in config:
        print("Unknown setting.")
        return
    new_val = "false" if config[flag] == "true" else "true"
    set_key(CONFIG_PATH, flag, new_val)
    print(f"Toggled {flag} → {new_val}")
    cli_log(f"Toggled {flag} → {new_val}")

#
# ─────────────────────────────────────────
# Section: CLI Main Loop
# ─────────────────────────────────────────
#
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
        elif cmd == "preset":
            change_preset()
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
