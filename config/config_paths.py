from pathlib import Path

# Root of the whole repo
ROOT = Path(__file__).resolve().parents[1]

# --- Shared directories ---
OPERATIONS_PATH = ROOT / "operations"
INTERFACES_PATH = ROOT / "interfaces"
SESSIONS_PATH = ROOT / "sessions"
LOGS_PATH = ROOT / "data/logs"
BUTTON_TRIGGER_LOG = LOGS_PATH / "button_trigger.log"
CONFIG_PATH = ROOT / "config" / "config.env"

# --- This project's app layer (custom per project) ---
APP_NAME = "timelapse"
APP_PATH = ROOT / APP_NAME
FUNCTIONS_PATH = APP_PATH / "functions"

# --- App-specific tools (defined by this project only) ---
START_SCRIPT = FUNCTIONS_PATH / "start_timelapse.py"
STATUS_SCRIPT = FUNCTIONS_PATH / "status_timelapse.py"
STOP_SCRIPT = FUNCTIONS_PATH / "stop_timelapse.py"
RUNNER_SCRIPT = FUNCTIONS_PATH / "timelapse_runner.py"
PHOTO_SCRIPT = FUNCTIONS_PATH / "take_photo.py"

TEMP_PATH = ROOT / "data/temp"

# Status logs path
STATUS_LOGS_PATH = ROOT / "data" / "statuslogs"

# --- Config + Preset Logic ---
CONFIG_DIR = ROOT / "config"
PRESETS_FILE = CONFIG_DIR / "presets.env"
MODE_CONTROL_FILE = CONFIG_DIR / "mode_control.env"
LOAD_PRESET_SCRIPT = CONFIG_DIR / "load_preset.sh"

# --- Session management ---
SESSIONMGMT_PATH = ROOT / "timelapse" / "sessionmgmt"