


# test_session_flow.py
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from timelapse.functions import start_timelapse
from timelapse.sessionmgmt.session_manager import (
    get_active_session,
    clear_active_session,
)
from config.config_paths import TEMP_PATH

print("▶️ Running test: test_session_flow")

# Start a timelapse session programmatically
print("📦 Simulating timelapse start...")
start_timelapse.main(simulate=True)  # Assumes simulate=True bypasses user input (if not implemented yet, we’ll add it)

# Give the system a moment (if needed)
time.sleep(1)

# Check if active session was set
active_session_path = get_active_session()
assert active_session_path is not None, "❌ Active session was not set"
print("✅ Active session set:", active_session_path)

# Check that the file exists
session_file = TEMP_PATH / "active_session.json"
assert session_file.exists(), f"❌ Expected session file not found at {session_file}"

# Clean up
clear_active_session()
assert not session_file.exists(), "❌ Session file was not cleared"
print("🧹 Cleaned up session file")