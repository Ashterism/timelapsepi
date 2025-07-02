"""
Test script to verify status and stop commands in the timelapse flow.

This test:
1. Launches a new timelapse session with short interval and low photo count.
2. Checks the session status after the first photo is taken.
3. Sends a stop command to end the session early.
4. Confirms that the active session file has been cleared and no further photos are taken.
"""

from pathlib import Path
import subprocess
import time
import sys

print("🔧 Running test_status_and_stop.py...")

BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_PATH = BASE_DIR / "data" / "temp"
ACTIVE_SESSION_PATH = TEMP_PATH / "active_session.json"

sys.path.append(str(BASE_DIR))
from config.config_paths import STATUS_SCRIPT, STOP_SCRIPT, START_SCRIPT

def file_exists():
    return ACTIVE_SESSION_PATH.exists()

def run_script(script_path, input_lines=None):
    input_data = "\n".join(input_lines) + "\n" if input_lines else None

    p = subprocess.Popen(
        ["python3", str(script_path)],
        cwd=BASE_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give subprocess a moment to start
    time.sleep(0.5)

    try:
        stdout, stderr = p.communicate(input=input_data, timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        stdout, stderr = p.communicate()
        print("❌ TimeoutExpired — killed process")

    print(f"🔁 STDOUT:\n{stdout}")
    print(f"⚠️ STDERR:\n{stderr}")
    return stdout, stderr

# Step 1: Start a new session
if file_exists():
    ACTIVE_SESSION_PATH.unlink()
    print("🧹 Cleared old active_session.json")

print("🚀 Launching start_timelapse.py")
inputs = ["00:00:03", "", "1", "3", ""]
run_script(START_SCRIPT, inputs)

# Step 2: Wait until at least one photo is taken
print("⏱ Waiting 2 seconds for session to begin...")
time.sleep(2)

print("📋 Checking status...")
status_output, _ = run_script(STATUS_SCRIPT)
print(status_output)

if "Active session:" in status_output:
    print("✅ Status script correctly detected active session.")
else:
    print("❌ Status script did not detect active session.")

# Step 3: Send stop command
print("🛑 Sending stop command...")
stop_output, _ = run_script(STOP_SCRIPT)
print(stop_output)

time.sleep(1)

# Step 4: Confirm active session is cleared
if not file_exists():
    print("✅ active_session.json successfully cleared.")
else:
    print("❌ active_session.json still exists.")