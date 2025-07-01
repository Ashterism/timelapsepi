import json
from pathlib import Path

from config.config_paths import TEMP_PATH

# Path to the temporary JSON file tracking the active session
ACTIVE_SESSION_FILE = TEMP_PATH / "active_session.json"

def get_active_session() -> Path | None:
    """Return the path of the active session folder, or None if not set or missing."""
    if not ACTIVE_SESSION_FILE.exists():
        return None
    try:
        with open(ACTIVE_SESSION_FILE) as f:
            data = json.load(f)
        session_path = Path(data["path"]).expanduser().resolve()
        if not session_path.exists():
            print(f"[session_manager] Session path not found: {session_path}")
            return None
        return session_path
    except Exception as e:
        print(f"[session_manager] Failed to load active session: {e}")
        return None

# Set the active session by saving its path to disk
def set_active_session(session_path: Path):
    """Save the active session path to file."""
    ACTIVE_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump({"path": str(session_path)}, f)

# Clear the stored active session
def clear_active_session():
    """Remove the active session file."""
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()

# Return session status (e.g., photo count, completion) from config
def get_session_status():
    """Return status dictionary from the active session config, or None if unavailable."""
    active_path = get_active_session()
    if not active_path:
        return None

    config_file = active_path / "timelapse_config.json"
    if not config_file.exists():
        return None

    try:
        with open(config_file) as f:
            config = json.load(f)
        return config.get("status", None)
    except Exception:
        return None