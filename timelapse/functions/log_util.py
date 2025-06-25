from pathlib import Path
import datetime
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from config_paths import LOGS_PATH

def log(msg, logfile_name="timelapse_general.log"):
    timestamp = datetime.datetime.now().isoformat()
    log_path = LOGS_PATH / logfile_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{timestamp} - {msg}\n")
