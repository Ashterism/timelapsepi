# take_photo.py — shared photo capture logic for CLI and Webapp

#!/usr/bin/env python3

import os
import json
from datetime import datetime
from pathlib import Path
import subprocess
import shutil

from config.config_paths import TEMP_PATH
from timelapse.functions.log_util import log

from timelapse.sessionmgmt.session_manager import get_active_session

LATEST_DIR = TEMP_PATH / "latestjpg"
LATEST_IMAGE = LATEST_DIR / "latest.jpg"
LATEST_METADATA = LATEST_DIR / "latest.json"

def take_photo(config=None):
    """Captures a test or timelapse photo using libcamera and writes metadata."""
    LATEST_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    temp_photo_path = LATEST_DIR / filename

    # Insert: Ensure config is a dict and get folder from active session if needed
    if config is None:
        config = {}

    if "folder" not in config:
        active_session = get_active_session()
        if active_session:
            config["folder"] = str(active_session)

    # Take photo to timestamped temp location
    cmd = ["libcamera-jpeg", "-o", str(temp_photo_path)]
    result = subprocess.run(cmd)

    if result.returncode != 0:
        log("[ERROR] Photo capture failed")
        return False

    # Update latest.jpg
    shutil.copy2(temp_photo_path, LATEST_IMAGE)
    log(f"[INFO] Test photo captured: {LATEST_IMAGE}")
    write_metadata(timestamp, temp_photo_path)

    # If it's a timelapse, also save to session folder
    if config and "folder" in config:
        session_folder = Path(config["folder"])
        session_folder.mkdir(parents=True, exist_ok=True)
        session_image_path = session_folder / filename
        shutil.copy2(temp_photo_path, session_image_path)
        write_metadata(timestamp, session_image_path)

    return True

def extract_exif_value(tag, file):
    try:
        result = subprocess.run(["exiftool", f"-{tag}", "-s3", str(file)], capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else "unknown"
    except Exception:
        return "unknown"

def write_metadata(timestamp, image_path):
    meta = {
        "filename": image_path.name,
        "timestamp": timestamp,
        "latest": image_path == LATEST_IMAGE,
        "camera": extract_exif_value("Model", image_path),
        "settings": {
            "iso": extract_exif_value("ISO", image_path),
            "shutter_speed": extract_exif_value("ExposureTime", image_path),
            "aperture": extract_exif_value("Aperture", image_path),
            "exposure_bias": extract_exif_value("ExposureCompensation", image_path),
            "focal_length": extract_exif_value("FocalLength", image_path),
            "metering_mode": extract_exif_value("MeteringMode", image_path),
            "flash": extract_exif_value("Flash", image_path),
            "white_balance": extract_exif_value("WhiteBalance", image_path),
            "image_width": extract_exif_value("ImageWidth", image_path),
            "image_height": extract_exif_value("ImageHeight", image_path),
            "file_size": extract_exif_value("FileSize", image_path)
        }
    }

    output_path = LATEST_METADATA if image_path == LATEST_IMAGE else image_path.with_suffix(".json")
    with open(output_path, "w") as f:
        json.dump(meta, f, indent=2)
    log(f"[INFO] Metadata saved: {output_path}")

if __name__ == "__main__":
    take_photo()

    
# TODO: Consider adding HDR support with:
# libcamera-still --hdr 1 ...
# Requires tuning + validation