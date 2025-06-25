from pathlib import Path
import datetime

def log(msg, logfile_name="timelapse_general.log"):
    timestamp = datetime.datetime.now().isoformat()
    log_path = Path("/home/ash/timelapse/data/logs") / logfile_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{timestamp} - {msg}\n")