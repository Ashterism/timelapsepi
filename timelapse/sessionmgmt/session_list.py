

import os
from pathlib import Path
from config.config_paths import SESSIONS_PATH, TEMP_PATH

def get_active_session_path():
    active_file = TEMP_PATH / "active_session.txt"
    if active_file.exists():
        with open(active_file, "r") as f:
            return f.read().strip()
    return None

def list_sessions():
    if not SESSIONS_PATH.exists():
        return []

    sessions = sorted(
        [p for p in SESSIONS_PATH.iterdir() if p.is_dir()],
        key=os.path.getmtime,
        reverse=True
    )

    active_session = get_active_session_path()
    result = []

    for session in sessions:
        is_active = session.as_posix() == active_session
        result.append({
            "path": session,
            "is_active": is_active
        })

    return result

if __name__ == "__main__":
    for session in list_sessions():
        flag = "🟢" if session["is_active"] else "⚪"
        print(f"{flag} {session['path']}")