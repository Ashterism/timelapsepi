#!/usr/bin/env python3

DEBUG_MODE = True

def debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

# Add repo root to sys.path dynamically
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import os
import uuid
import datetime
from pathlib import Path
import subprocess
from config.config_paths import SESSIONS_PATH, RUNNER_SCRIPT
from timelapse.functions.log_util import log
from timelapse.sessionmgmt.session_manager import get_active_session, set_active_session

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

def start_session_from_config(config: dict) -> Path:
    config_path = Path(config["folder"]) / "timelapse_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    set_active_session(Path(config["folder"]))
    log(f"Active session set: {Path(config['folder'])}", "timelapse_start.log")

    process = subprocess.Popen([
        "python3", str(RUNNER_SCRIPT), str(config_path)
    ])
    pid_file = Path(config["folder"]) / "runner.pid"
    with open(pid_file, "w") as f:
        f.write(str(process.pid))

    log(f"Runner PID saved: {process.pid}", "timelapse_start.log")

    metadata = {
        "status": "running",
        "started": datetime.datetime.now().isoformat(),
        "ended": None,
        "interval_sec": config["interval_sec"]
    }
    metadata_path = Path(config["folder"]) / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return Path(config["folder"])

def main():
    print("🎞  Timelapse Setup")

    if get_active_session():
        active_file = TEMP_PATH / "active_session.json"

        print("❌ A session is already active. Stop it before starting a new one.")
        sys.exit(1)

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
        "interval_sec": interval_sec,
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

    start_session_from_config(config)

def main_from_web(config: dict) -> Path:
    debug(f"Incoming config in main_from_web: {config}")
    if get_active_session():
        print("❌ A session is already active. Stop it before starting a new one.")
        sys.exit(1)

    SESSIONS_PATH.mkdir(parents=True, exist_ok=True)

    interval_str = config.get("interval")
    try:
        h, m, s = map(int, interval_str.strip().split(":"))
        interval_sec = h * 3600 + m * 60 + s
    except Exception:
        print("⚠️ Invalid interval format.")
        sys.exit(1)

    start_time = config.get("start_time") or datetime.datetime.now().isoformat()
    end_type = config.get("end_type")
    count = config.get("count")
    end_time = config.get("end_time")

    if end_type == "photo_count":
        end_condition = "count"
    elif end_type == "end_time":
        end_condition = "time"
    else:
        print("⚠️ Invalid end type.")
        sys.exit(1)

    folder = config.get("folder", "").strip()
    if not folder:
        folder = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S")
    folder_path = SESSIONS_PATH / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    final_config = {
        "id": str(uuid.uuid4()),
        "created": datetime.datetime.now().isoformat(),
        "interval_sec": interval_sec,
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

    return start_session_from_config(final_config)

if __name__ == "__main__":
    main()