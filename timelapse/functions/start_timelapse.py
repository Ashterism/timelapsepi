#!/usr/bin/env python3

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

def main():
    print("🎞  Timelapse Setup")

    if get_active_session():
        active_file = TEMP_PATH / "active_session.json"

        print("\n[DEBUG] Active session detected.")
        if active_file.exists():
            print(f"✅ Found: {active_file}")
            print("📄 Contents:", active_file.read_text())
        else:
            print(f"❌ active_session.json not found at expected path: {active_file}")

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

    # Mark this session as active by writing to active_session.json
    set_active_session(folder_path)
    log(f"Active session set: {folder_path}", "timelapse_start.log")

    print("🚀 Launching timelapse runner...")

    # Launch the runner and save its PID
    process = subprocess.Popen([
        "python3", str(RUNNER_SCRIPT), str(config_path)
    ])

    pid_file = folder_path / "runner.pid"
    with open(pid_file, "w") as f:
        f.write(str(process.pid))

    log(f"Runner PID saved: {process.pid}", "timelapse_start.log")

    # Write metadata.json to track session state
    metadata = {
        "status": "running",
        "started": datetime.datetime.now().isoformat(),
        "ended": None,
        "interval_seconds": interval_sec
    }
    metadata_path = folder_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    main()