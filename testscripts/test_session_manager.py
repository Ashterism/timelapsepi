import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # Adds project root to Python path
from config.config_paths import TEMP_PATH, SESSIONS_PATH


from timelapse.sessionmgmt.session_manager import (
    set_active_session,
    get_active_session,
    clear_active_session,
)

# Create a dummy session path
dummy_session_path = SESSIONS_PATH / "test_session"
dummy_config_path = dummy_session_path / "timelapse_config.json"
dummy_session_path.mkdir(parents=True, exist_ok=True)

# Create a mock config file
with open(dummy_config_path, "w") as f:
    json.dump({"status": {"photos_taken": 1, "total_photos": 5}}, f)

# Test set_active_session
print("Setting active session...")
set_active_session(dummy_session_path)
assert (TEMP_PATH / "active_session.txt").exists(), "❌ active_session.txt was not created"

# Test get_active_session
print("Getting active session...")
active = get_active_session()
assert active == dummy_session_path, "❌ Active session path mismatch"
print("✅ Active session:", active)

# Test get_session_status
from timelapse.sessionmgmt.session_manager import get_session_status
status = get_session_status()
assert status == {"photos_taken": 1, "total_photos": 5}, "❌ Incorrect status read from config"
print("📸 Status:", status)

# Clean up
clear_active_session()
assert not (TEMP_PATH / "active_session.txt").exists(), "❌ active_session.txt was not cleared"
print("🧹 Cleared active session.")
