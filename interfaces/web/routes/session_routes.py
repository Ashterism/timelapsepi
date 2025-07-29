from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from timelapse.sessionmgmt.session_list import list_sessions

router = APIRouter()

@router.get("/sessions")
def get_sessions():
    return list_sessions()

@router.get("/session-images")
def list_session_images(path: str = Query(...)):
    session_path = Path(path)
    if not session_path.exists():
        return {"error": "Invalid session path"}

    images = sorted([
        f.name for f in session_path.iterdir()
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg']
    ])
    return {"images": images}


# New route: /session-metadata
@router.get("/session-metadata")
def session_metadata(path: str = Query(...)):
    session_path = Path(path)
    if not session_path.exists() or not session_path.is_dir():
        return JSONResponse(status_code=400, content={"error": "Invalid session path"})

    metadata_json_path = session_path / "metadata.json"
    config_json_path = session_path / "timelapse_config.json"
    try:
        with open(metadata_json_path, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": f"Could not read metadata.json: {str(e)}"})
    try:
        with open(config_json_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": f"Could not read timelapse_config.json: {str(e)}"})

    # Folder: from config, or fallback to folder name
    folder = config.get("folder") or session_path.name
    # Started/ended from metadata
    started = metadata.get("started")
    ended = metadata.get("ended") if "ended" in metadata else None
    # Interval: prefer interval_seconds from config, fallback to metadata
    interval = (
        config.get("interval_seconds")
        or metadata.get("interval_seconds")
        or config.get("interval")
        or metadata.get("interval")
        or None
    )
    # image_count from config["status"]["photos_taken"] if present
    image_count = None
    status = config.get("status", {})
    if isinstance(status, dict):
        image_count = status.get("photos_taken")

    return {
        "folder": folder,
        "started": started,
        "ended": ended,
        "interval": interval,
        "image_count": image_count,
    }