import subprocess
import json
import time
from pathlib import Path

print("🔧 Running test_timelapse_flow.py...")

BASE_DIR = Path(__file__).resolve().parents[1]
TEMP_PATH = BASE_DIR / "data" / "temp"
SESSIONS_PATH = BASE_DIR / "sessions"
ACTIVE_SESSION_FILE = TEMP_PATH / "active_session.json"

# 1. Clear old active session if exists
if ACTIVE_SESSION_FILE.exists():
    ACTIVE_SESSION_FILE.unlink()
    print("🧹 Cleared old active_session.json")

# 2. Run start_timelapse.py (make sure it's runnable and uses correct paths)
print("🚀 Launching start_timelapse.py")
import threading

p = subprocess.Popen(
    ["python3", "timelapse/functions/start_timelapse.py"],
    cwd=BASE_DIR,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

inputs = "\n".join([
    "00:00:01",  # Interval
    "",          # Start time
    "1",         # End condition: number of photos
    "2",         # Number of photos
    ""           # Folder name
]) + "\n"

def feed_input(proc, text):
    try:
        proc.stdin.write(text)
        proc.stdin.flush()
    except Exception as e:
        print("❌ Input write error:", e)

input_thread = threading.Thread(target=feed_input, args=(p, inputs))
input_thread.start()

for line in p.stdout:
    print(line.strip())
    if "Photo taken 1 of" in line:
        if ACTIVE_SESSION_FILE.exists():
            print("✅ active_session.json exists after first photo")
        else:
            print("❌ active_session.json missing after first photo")

p.wait(timeout=30)

# 3. Check for new active_session.json
# if not ACTIVE_SESSION_FILE.exists():
#     print("❌ active_session.json not found after running start_timelapse.py")
#     exit(1)

if ACTIVE_SESSION_FILE.exists():
    print("❌ active_session.json still exists after runner completed")
    exit(1)
else:
    print("✅ active_session.json successfully cleared after completion")

print("✅ Test finished. You can now observe timelapse_runner logs for behaviour.")