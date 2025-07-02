#!/usr/bin/env python3

import json
import subprocess
import time
import sys
import datetime
from pathlib import Path
from log_util import log
from config.config_paths import PHOTO_SCRIPT, TEMP_PATH
from timelapse.sessionmgmt.session_manager import set_active_session
from timelapse.functions.take_photo import take_photo
from timelapse.sessionmgmt.session_manager import get_active_session

# TEMP DEBUG
from config.config_paths import TEMP_PATH
print(f"[DEBUG] TEMP_PATH = {TEMP_PATH}")
# TEMP DEBUG

def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        log(f"❌ Failed to load config: {e}", "timelapse_runner.log")
        sys.exit(1)

def save_config(config, config_path):
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log(f"❌ Failed to update config: {e}", "timelapse_runner.log")

def should_continue(config):
    if config["end_condition"] == "count":
        return config["status"]["photos_taken"] < config["photo_count"]
    elif config["end_condition"] == "time":
        now = datetime.datetime.now()
        end_time = datetime.datetime.fromisoformat(config["end_time"])
        return now < end_time
    return False

def wait_until(start_time_iso):
    start_time = datetime.datetime.fromisoformat(start_time_iso)
    now = datetime.datetime.now()
    seconds = (start_time - now).total_seconds()
    if seconds > 0:
        log(f"⏳ Waiting {int(seconds)} seconds until start time...", "timelapse_runner.log")
        time.sleep(seconds)

# checks if active session file still exists (stop/complete removes it)
def not_cancelled(config):
    active = get_active_session()
    print(f"[DEBUG] not_cancelled: active = {active}, config = {config['folder']}")
    return active and str(active) == str(config["folder"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 timelapse_runner.py <config_path>")
        sys.exit(1)
    config_path = Path(sys.argv[1])
    config = load_config(config_path)

    config["status"]["started"] = True
    save_config(config, config_path)

    set_active_session(config["folder"])
    log(f"📂 Timelapse session started: {config['folder']}", "timelapse_runner.log")
    wait_until(config["start_time"])

    interval = config["interval_seconds"]
    total = config["photo_count"]

    print(f"[DEBUG] Starting loop? photos_taken = {config['status']['photos_taken']}, photo_count = {config['photo_count']}")
    print(f"[DEBUG] should_continue = {should_continue(config)}")

    while should_continue(config):
        print(f"[DEBUG] ⬅️ ENTERED LOOP — photos_taken = {config['status']['photos_taken']}, should_continue = {should_continue(config)}")
        if not not_cancelled(config):
            log("🛑 Session manually stopped or invalid. Exiting timelapse runner.", "timelapse_runner.log")
            break
        success = take_photo(config)
        if success:
            config["status"]["photos_taken"] += 1
            save_config(config, config_path)
            taken = config["status"]["photos_taken"]
            total = config["photo_count"]
            log(f"📸 Photo taken ({taken}/{total})", "timelapse_runner.log")
            if taken < total:
                print(f"📸 Photo taken {taken} of {total} — waiting {config['interval_seconds']}s...")
            else:
                print(f"✅ All {total} photos taken. Timelapse complete.")
            log(f"⏳ Waiting {config['interval_seconds']} seconds for next photo...", "timelapse_runner.log")
        else:
            log("❌ Photo failed", "timelapse_runner.log")

        time.sleep(config["interval_seconds"])

    log("✅ Timelapse complete.", "timelapse_runner.log")
    config["status"]["completed"] = True
    save_config(config, config_path)

    from timelapse.sessionmgmt.session_manager import clear_active_session
    clear_active_session()

if __name__ == "__main__":
    main()
