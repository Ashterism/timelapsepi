#!/usr/bin/env python3

import json
import sys
from pathlib import Path
import datetime
from log_util import log
from config.config_paths import LOGS_PATH  

def print_status(config_path):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        log(f"✅ Loaded config: {config_path}", "timelapse_status.log")
    except Exception as e:
        log(f"❌ Failed to load config: {e}", "timelapse_status.log")
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)

    folder = config.get("folder", "Unknown")
    interval = config.get("interval_seconds", "?")
    start_time = config.get("start_time", "?")
    end_time = config.get("end_time", "?")
    photo_count = config["status"].get("photos_taken", 0)
    completed = config["status"].get("completed", False)

    print(f"📂 Folder: {folder}")
    print(f"🕒 Interval: {interval} seconds")
    print(f"⏰ Start Time: {start_time}")
    if config["end_condition"] == "count":
        total = config.get("photo_count", "?")
        print(f"📸 Photos Taken: {photo_count} / {total}")
    else:
        print(f"🛑 End Time: {end_time}")
        print(f"📸 Photos Taken: {photo_count}")

    if "completed" in config["status"]:
        print(f"✅ Completed: {'Yes' if config['status']['completed'] else 'No'}")
    else:
        print(f"✅ Completed: Unknown (status not updated)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 status_timelapse.py <path_to_config.json>")
        sys.exit(1)

    print_status(Path(sys.argv[1]))