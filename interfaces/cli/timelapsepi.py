#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values, set_key

from timelapse.sessionmgmt.session_manager import get_active_session, set_active_session

# Allow importing from project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config.config_paths import (
    CONFIG_PATH, TEMP_PATH, SESSIONS_PATH, PHOTO_SCRIPT,
    START_SCRIPT, STATUS_SCRIPT, STOP_SCRIPT, LOAD_PRESET_SCRIPT
)

# Also allow log_util import
sys.path.append(str(Path(__file__).resolve().parents[2] / "timelapse/sessionmgt"))
from timelapse.functions.log_util import log

config = dotenv_values(CONFIG_PATH)
WIFI_MODES = ["client", "hotspot", "none"]

# CLI logger
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
        print("0. Back")
    
    while True:
        show_menu()
        choice = input("Select preset [1-4] or 5 for info: ").strip()
        
        if choice == "0":
            print("↩️ Returning to main menu...")
            break

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
            result = subprocess.run(["bash", str(LOAD_PRESET_SCRIPT), preset])
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
    if get_active_session():
        print("❌ A session is already active. Stop it before starting a new one.")
        return
    try:
        subprocess.Popen(
            ["python3", str(START_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        run_status()
        print("✅ Timelapse run completed.")
        input("Press Enter to return to menu...")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        cli_log(f"Failed to start: {e}")

def run_status():
    active = get_active_session()
    if active:
        print(f"📂 Active session: {active}")
    else:
        print("ℹ️ No active session.")
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
                # Remove active_session.txt after stopping
                active_file = TEMP_PATH / "active_session.txt"
                if active_file.exists():
                    active_file.unlink()
                return
        print("⚠️ No running session found.")
    except Exception as e:
        print(f"❌ Error stopping session: {e}")
        cli_log(f"Stop failed: {e}")

def run_test_photo():
    if get_active_session():
        print("❌ A session is already active. Stop it before starting a new one.")
        return
    try:
        from timelapse.take_photo import take_photo
        success = take_photo()
        if not success:
            print("❌ Photo capture failed.")
            return

        from config.config_paths import TEMP_PATH
        latest_path = TEMP_PATH / "latestjpg" / "latest.jpg"
        metadata_path = TEMP_PATH / "latestjpg" / "latest.json"

        if not metadata_path.exists():
            print("❌ Photo taken but metadata missing.")
            return

        import json
        with open(metadata_path) as f:
            metadata = json.load(f)
        timestamp = metadata.get("timestamp", "unknown")
        print(f"\n📸 Test photo captured.")
        print(f"🕒 Timestamp: {timestamp}")
        print(f"📂 Path: {latest_path}")
        print(f"💻 Mac copy command:")
        print(f"scp pi@raspberrypi.local:{latest_path} ~/Downloads/")
    except Exception as e:
        print(f"❌ Error during test photo: {e}")
        cli_log(f"Test photo error: {e}")

#
# ─────────────────────────────────────────
# Section: Config Flag Toggling
# ─────────────────────────────────────────
#
def toggle_flag(flag):
    if not flag or flag not in config:
        print("❓ Usage: toggle <SETTING_NAME>")
        print("Available toggles:")
        for k, v in config.items():
            if v in ["true", "false"]:
                print(f"  {k} → currently {v}")
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
        elif cmd.startswith("toggle"):
            parts = cmd.split(" ", 1)
            flag = parts[1].strip().upper() if len(parts) > 1 else None
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
