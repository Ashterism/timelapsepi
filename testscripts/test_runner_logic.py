"""
Test script to directly step through timelapse_runner logic.

Purpose:
- Simulate a valid config/session being in place
- Call timelapse_runner.main() directly
- Intercept and verify session status updates
- Confirm correct handling of start, loop, and completion logic without waiting for real photos
"""

import sys
import json
import time
from pathlib import Path

# Ensure project root is in path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from timelapse.sessionmgmt.session_manager import (
    set_active_session,
    get_active_session,
    clear_active_session,
)
# Add functions dir to sys.path for log_util.py
sys.path.append(str(Path(__file__).resolve().parents[1] / "timelapse/functions"))
from timelapse.functions import timelapse_runner
from timelapse.functions.take_photo import take_photo
from config.config_paths import TEMP_PATH, SESSIONS_PATH

# Prep test session
test_session_path = SESSIONS_PATH / "test_runner_logic"
test_config_path = test_session_path / "timelapse_config.json"
test_session_path.mkdir(parents=True, exist_ok=True)

dummy_config = {
    "interval_seconds": 1,
    "start_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "folder": str(test_session_path),
    "end_condition": "count",
    "photo_count": 2,
    "status": {
        "photos_taken": 0,
        "total_photos": 2
    }
}

with open(test_config_path, "w") as f:
    json.dump(dummy_config, f)

set_active_session(test_session_path)

print("▶️ Running timelapse_runner.main() with test config...")

# Simulate command line invocation by setting sys.argv
sys.argv = ["timelapse_runner.py", str(test_config_path)]
timelapse_runner.main()
time.sleep(2)

# Validate results
with open(test_config_path) as f:
    final_config = json.load(f)
final_status = final_config.get("status")
print("🧐 Final config status:", final_status)
assert final_status is not None, "❌ Session status is None — possibly not written correctly."
assert final_status["photos_taken"] == 2, f"❌ Expected 2 photos, got {final_status['photos_taken']}"
print("✅ Photos taken:", final_status["photos_taken"])

# Clean up
clear_active_session()
assert not (TEMP_PATH / "active_session.json").exists(), "❌ Session file not cleared"
print("🧹 Cleaned up session")