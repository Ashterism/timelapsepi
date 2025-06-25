from pathlib import Path

# Root of the whole repo
ROOT = Path(__file__).resolve().parent

# --- Shared directories ---
OPERATIONS_PATH = ROOT / "operations"
INTERFACES_PATH = ROOT / "interfaces"
SESSIONS_PATH = ROOT / "sessions"
LOGS_PATH = ROOT / "data/logs"
CONFIG_PATH = OPERATIONS_PATH / "config.env"

# --- This project's app layer (custom per project) ---
APP_NAME = "timelapse"
APP_PATH = ROOT / APP_NAME
FUNCTIONS_PATH = APP_PATH / "functions"

# --- App-specific tools (defined by this project only) ---
START_SCRIPT = FUNCTIONS_PATH / "start_timelapse.py"
STATUS_SCRIPT = FUNCTIONS_PATH / "status_timelapse.py"
STOP_SCRIPT = FUNCTIONS_PATH / "stop_timelapse.py"
RUNNER_SCRIPT = FUNCTIONS_PATH / "timelapse_runner.py"
PHOTO_SCRIPT = FUNCTIONS_PATH / "photo.sh"
