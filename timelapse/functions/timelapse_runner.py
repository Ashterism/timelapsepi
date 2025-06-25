#!/usr/bin/env python3

import json
import subprocess
import time
import datetime
from pathlib import Path
import sys

# Add shared utility path
sys.path.append(str(Path(__file__).resolve().parents[2] ))
from log_util import log
from config_paths import PHOTO_SCRIPT

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

def take_photo():
    result = subprocess.run(["bash", str(PHOTO_SCRIPT)])
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 timelapse_runner.py <config_path>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = load_config(config_path)

    log(f"📂 Timelapse session started: {config['folder']}", "timelapse_runner.log")
    wait_until(config["start_time"])

    config["status"]["started"] = True
    save_config(config, config_path)

    while should_continue(config):
        success = take_photo()
        if success:
            config["status"]["photos_taken"] += 1
            save_config(config, config_path)
            log(f"📸 Photo taken ({config['status']['photos_taken']})", "timelapse_runner.log")
        else:
            log("❌ Photo failed", "timelapse_runner.log")

        time.sleep(config["interval_seconds"])

    log("✅ Timelapse complete.", "timelapse_runner.log")
    config["status"]["completed"] = True
    save_config(config, config_path)

if __name__ == "__main__":
    main()
