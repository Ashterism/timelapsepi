

import json
from pathlib import Path

from config.config_paths import TEMP_PATH

ACTIVE_SESSION_FILE = TEMP_PATH / "active_session.json"

def get_active_session() -> Path | None:
    """Return the path of the active session folder, or None if not set or missing."""
    if not ACTIVE_SESSION_FILE.exists():
        return None
    try:
        with open(ACTIVE_SESSION_FILE) as f:
            data = json.load(f)
        session_path = Path(data["path"])
        return session_path if session_path.exists() else None
    except Exception:
        return None

def set_active_session(session_path: Path):
    """Save the active session path to file."""
    ACTIVE_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump({"path": str(session_path)}, f)

def clear_active_session():
    """Remove the active session file."""
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()