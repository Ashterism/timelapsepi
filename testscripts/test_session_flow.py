"""
Test script for simulating the full timelapse session creation flow.

This script:
- Simulates CLI input to start a new timelapse session
- Validates that active_session.json is created and contains the correct path
- Checks that the session folder and config file are created correctly
- Asserts that the config file has the expected total photo count
- Cleans up the session and ensures session data is cleared

Purpose: Confirm that end-to-end session setup logic behaves correctly when triggered via subprocess.
"""
# test_full_start.py
import sys
import json
import time
import subprocess
from pathlib import Path

# Manually add project root
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import paths and session utilities
from timelapse.sessionmgmt.session_manager import (
    get_active_session,
    clear_active_session,
)
from config.config_paths import TEMP_PATH

print("▶️ Running test: test_full_start")

# Simulate CLI input for starting a timelapse
print("📦 Simulating timelapse start via subprocess...")
user_input = "00:00:15\n\n1\n2\n\n"
start_script = Path(__file__).resolve().parents[1] / "timelapse/functions/start_timelapse.py"
subprocess.run(["python3", str(start_script)], input=user_input, text=True)

# Allow time for session file to be written
time.sleep(1)

# Validate session creation
active_session_path = get_active_session()
assert active_session_path is not None, "❌ Active session was not set"
print("✅ Active session set:", active_session_path)

# Check the session file exists
session_file = TEMP_PATH / "active_session.json"
assert session_file.exists(), f"❌ Expected session file not found at {session_file}"

# Validate contents of active_session.json
with open(session_file) as f:
    session_data = json.load(f)
assert session_data["path"] == str(active_session_path), "❌ Session path mismatch in file"

# Confirm session folder exists
assert active_session_path.exists(), "❌ Active session folder does not exist"

# Confirm session config file exists
config_file = active_session_path / "timelapse_config.json"
assert config_file.exists(), "❌ Config file not created in session folder"

# Confirm config file contains expected total photo count
with open(config_file) as f:
    config = json.load(f)
assert config["status"]["total_photos"] == 2, "❌ Total photo count mismatch"

# Clean up
clear_active_session()
assert not session_file.exists(), "❌ Session file was not cleared"
print("🧹 Cleaned up session file")