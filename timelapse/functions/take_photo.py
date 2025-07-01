# take_photo.py — shared photo capture logic for CLI and Webapp

import os
import json
from datetime import datetime
from pathlib import Path
import subprocess

from config.config_paths import TEMP_PATH
from timelapse.functions.log_util import log

LATEST_DIR = TEMP_PATH / "latestjpg"
LATEST_IMAGE = LATEST_DIR / "latest.jpg"
LATEST_METADATA = LATEST_DIR / "latest.json"

def take_photo(config=None):
    """Captures a test photo using libcamera and writes metadata."""
    LATEST_DIR.mkdir(parents=True, exist_ok=True)

    # Take photo
    cmd = ["libcamera-jpeg", "-o", str(LATEST_IMAGE)]
    result = subprocess.run(cmd)

    if result.returncode != 0:
        log("[ERROR] Photo capture failed")
        return False

    timestamp = datetime.now().isoformat()
    log(f"[INFO] Test photo captured: {LATEST_IMAGE}")
    write_metadata(timestamp)
    return True

def extract_exif_value(tag, file):
    try:
        result = subprocess.run(["exiftool", f"-{tag}", "-s3", str(file)], capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else "unknown"
    except Exception:
        return "unknown"

def write_metadata(timestamp):
    meta = {
        "filename": LATEST_IMAGE.name,
        "timestamp": timestamp,
        "latest": True,
        "camera": extract_exif_value("Model", LATEST_IMAGE),
        "settings": {
            "iso": extract_exif_value("ISO", LATEST_IMAGE),
            "shutter_speed": extract_exif_value("ExposureTime", LATEST_IMAGE),
            "aperture": extract_exif_value("Aperture", LATEST_IMAGE),
            "exposure_bias": extract_exif_value("ExposureCompensation", LATEST_IMAGE),
            "focal_length": extract_exif_value("FocalLength", LATEST_IMAGE),
            "metering_mode": extract_exif_value("MeteringMode", LATEST_IMAGE),
            "flash": extract_exif_value("Flash", LATEST_IMAGE),
            "white_balance": extract_exif_value("WhiteBalance", LATEST_IMAGE),
            "image_width": extract_exif_value("ImageWidth", LATEST_IMAGE),
            "image_height": extract_exif_value("ImageHeight", LATEST_IMAGE),
            "file_size": extract_exif_value("FileSize", LATEST_IMAGE)
        }
    }

    with open(LATEST_METADATA, "w") as f:
        json.dump(meta, f, indent=2)

    log(f"[INFO] Metadata saved: {LATEST_METADATA}")