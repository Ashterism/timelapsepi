

import subprocess
import time
import json
from pathlib import Path
from timelapse.config.config_paths import TEMP_PATH
from timelapse.sessionmgmt.session_manager import clear_active_session

def test_start_timelapse_creates_valid_session():
    print("\n🚀 Running full test of start_timelapse.py with real folders...")

    # Ensure clean start
    clear_active_session()
    assert not (TEMP_PATH / "active_session.json").exists(), "❌ Pre-test: active_session.json still exists"

    # Run script
    result = subprocess.run(
        ["python3", "scripts/start_timelapse.py"],
        input=b"00:00:10\n\n3\n\n",  # interval, blank start, 3 photos, blank folder
        capture_output=True,
        timeout=10
    )

    print("🖨️ Script output:\n", result.stdout.decode())

    # Validate session creation
    active_path = TEMP_PATH / "active_session.json"
    assert active_path.exists(), "❌ active_session.json not created"
    with open(active_path) as f:
        session_path = Path(json.load(f)["path"])

    print("📁 Active session folder:", session_path)

    config_path = session_path / "timelapse_config.json"
    assert config_path.exists(), "❌ timelapse_config.json not found"
    with open(config_path) as f:
        config = json.load(f)

    assert config["status"]["started"] is False, "❌ started status should be False"
    assert config["status"]["photos_taken"] == 0, "❌ photos_taken should be 0"

    print("✅ Session and config validated.")

    # Clean up
    clear_active_session()
    print("🧹 Cleared active session.")