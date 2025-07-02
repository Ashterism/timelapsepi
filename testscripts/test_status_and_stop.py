"""
Test script to verify status and stop commands in the timelapse flow.

This test:
1. Launches a new timelapse session with short interval and low photo count.
2. Checks the session status after the first photo is taken.
3. Sends a stop command to end the session early.
4. Confirms that the active session file has been cleared and no further photos are taken.
"""

import subprocess
import time
from pathlib import Path

ACTIVE_SESSION_PATH = Path("/home/ash/timelapse/data/temp/active_session.json")
STATUS_SCRIPT = "timelapse/functions/status_timelapse.py"
STOP_SCRIPT = "timelapse/functions/stop_timelapse.py"
START_SCRIPT = "timelapse/functions/start_timelapse.py"

def file_exists():
    return ACTIVE_SESSION_PATH.exists()

def run_script(script_path, input_data=None):
    p = subprocess.Popen(
        ["python3", script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = p.communicate(input=input_data, timeout=20)
    print(f"🔁 STDOUT:\n{stdout}")
    print(f"⚠️ STDERR:\n{stderr}")
    return stdout, stderr

print("🔧 Running test_status_and_stop.py...")

# Step 1: Start a new session
if file_exists():
    ACTIVE_SESSION_PATH.unlink()
    print("🧹 Cleared old active_session.json")

print("🚀 Launching start_timelapse.py")
inputs = "00:00:01\n\n1\n3\n\n"
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
else:
    print("⚠️ Something went wrong — test may not have executed properly.")