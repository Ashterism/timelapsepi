#!/usr/bin/env python3

import json
import os
import uuid
import datetime
from pathlib import Path
import subprocess
import sys
from log_util import log


# Absolute base path (edit here if you change username or path)
BASE_PATH = Path("/home/ash/timelapse")
SESSIONS_PATH = BASE_PATH / "sessions"

def prompt_time(prompt, default_now=False):
    entry = input(prompt)
    if not entry.strip() and default_now:
        return datetime.datetime.now().isoformat()
    try:
        return datetime.datetime.fromisoformat(entry).isoformat()
    except ValueError:
        print("⚠️ Invalid format. Use YYYY-MM-DDTHH:MM:SS")
        sys.exit(1)

def prompt_interval():
    raw = input("Interval (hh:mm:ss): ")
    try:
        h, m, s = map(int, raw.strip().split(":"))
        return h * 3600 + m * 60 + s
    except Exception:
        print("⚠️ Invalid interval format.")
        sys.exit(1)

def main():
    print("🎞  Timelapse Setup")

    # Ensure sessions folder exists
    SESSIONS_PATH.mkdir(parents=True, exist_ok=True)

    interval_sec = prompt_interval()

    start_time = prompt_time("Start time (ISO format or blank for now): ", default_now=True)

    mode = input("End condition - (1) Number of photos or (2) End time? [1/2]: ").strip()
    if mode == "1":
        end_condition = "count"
        count = int(input("Number of photos to take: "))
        end_time = None
    elif mode == "2":
        end_condition = "time"
        count = None
        end_time = prompt_time("End time (ISO format): ")
    else:
        print("⚠️ Invalid choice.")
        sys.exit(1)

    folder = input("Folder name (leave blank to auto-generate): ").strip()
    if not folder:
        folder = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S")
    folder_path = SESSIONS_PATH / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    config = {
        "id": str(uuid.uuid4()),
        "created": datetime.datetime.now().isoformat(),
        "interval_seconds": interval_sec,
        "start_time": start_time,
        "end_condition": end_condition,
        "photo_count": count,
        "end_time": end_time,
        "folder": str(folder_path),
        "status": {
            "started": False,
            "photos_taken": 0
        }
    }

    config_path = folder_path / "timelapse_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Config saved: {config_path}")
    print("🚀 Launching timelapse runner...")

    # Launch the runner and save its PID
    process = subprocess.Popen([
        "nohup", "python3", str(BASE_PATH / "timelapse_runner.py"), str(config_path)
    ])

    pid_file = folder_path / "runner.pid"
    with open(pid_file, "w") as f:
        f.write(str(process.pid))

    log(f"Runner PID saved: {process.pid}", "timelapse_start.log")

if __name__ == "__main__":
    main()