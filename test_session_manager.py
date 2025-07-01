from pathlib import Path
import json

from timelapse.sessionmgmt.session_manager import (
    set_active_session,
    get_active_session,
    clear_active_session,
)

# Create a dummy session path
dummy_session_path = Path.home() / "timelapse/sessions/test_session"
dummy_config_path = dummy_session_path / "timelapse_config.json"
dummy_session_path.mkdir(parents=True, exist_ok=True)

# Create a mock config file
with open(dummy_config_path, "w") as f:
    json.dump({"status": {"photos_taken": 1, "total_photos": 5}}, f)

# Test set_active_session
print("Setting active session...")
set_active_session(dummy_session_path)

# Test get_active_session
print("Getting active session...")
active = get_active_session()
print("✅ Active session:", active)

# Test get_session_status
from timelapse.sessionmgmt.session_manager import get_session_status
status = get_session_status()
print("📸 Status:", status)

# Clean up
clear_active_session()
print("🧹 Cleared active session.")

# Optional: remove dummy session folder (if you're done with it)
# import shutil
# shutil.rmtree(dummy_session_path)