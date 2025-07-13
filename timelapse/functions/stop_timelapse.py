#!/usr/bin/env python3

import os
import signal
import sys
from pathlib import Path
from timelapse.functions.log_util import log

from config.config_paths import LOGS_PATH
from timelapse.sessionmgmt.session_manager import clear_active_session

def stop_runner(session_folder):
    pid_path = Path(session_folder) / "runner.pid"
    if not pid_path.exists():
        print("❌ No PID file found.")
        log(f"❌ No PID file found in {session_folder}", "timelapse_stop.log")
        sys.exit(1)

    try:
        with open(pid_path) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        print(f"🛑 Timelapse runner (PID {pid}) stopped.")
        log(f"🛑 Stopped runner PID {pid}", "timelapse_stop.log")
        pid_path.unlink()
        log("🧹 PID file removed.", "timelapse_stop.log")
        clear_active_session()
        log("📁 Cleared active session.", "timelapse_stop.log")
    except ProcessLookupError:
        print("⚠️ Process not found — may have already stopped.")
        log(f"⚠️ PID {pid} not found — already stopped?", "timelapse_stop.log")
        pid_path.unlink()
        clear_active_session()
        log("📁 Cleared active session.", "timelapse_stop.log")
    except Exception as e:
        print(f"❌ Error stopping process: {e}")
        log(f"❌ Error stopping PID {pid}: {e}", "timelapse_stop.log")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2 and not (len(sys.argv) == 2 and sys.argv[1] == "--auto"):
        print("Usage: python3 stop_timelapse.py <path_to_session_folder>")
        sys.exit(1)

    if sys.argv[1] == "--auto":
        from config.config_paths import TEMP_PATH, SESSIONS_PATH
        from timelapse.sessionmgmt.session_manager import get_active_session

        active_session = get_active_session()
        if not active_session:
            print("ℹ️ No active session.")
            sys.exit(0)

        pid_path = Path(active_session) / "timelapse_runner.pid"
        if pid_path.exists():
            stop_runner(active_session)
        else:
            print("⚠️ No runner PID file found. Cleaning up stale session.")
            clear_active_session()
            sys.exit(0)
    else:
        stop_runner(sys.argv[1])
