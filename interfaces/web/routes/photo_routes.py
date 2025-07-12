from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import os
import json
import logging

from config.config_paths import INTERFACES_PATH, PHOTO_SCRIPT, TEMP_PATH
from timelapse.sessionmgmt.session_manager import get_active_session

logger = logging.getLogger(__name__)
router = APIRouter()

logger.debug("✅ photo_routes.py router loaded")

@router.get("/latest.jpg")
def latest_jpg():
    path = TEMP_PATH / "latest.jpg"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    return FileResponse(path)

@router.get("/latest-timestamp")
def latest_timestamp():
    path = TEMP_PATH / "latest.json"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("timestamp", "")
    except Exception as e:
        logger.error(f"Error reading latest.json: {e}")
        return PlainTextResponse('', status_code=500)

@router.post("/photo")
def photo():
    logger.debug("📸 /photo route hit")
    session = get_active_session()
    if session:
        logger.warning("❌ Cannot take test photo: session is active.")
        return PlainTextResponse('❌ Session in progress. Stop it before taking a test photo.', status_code=400)

    result = subprocess.run(
        ['/bin/bash', str(PHOTO_SCRIPT)],
        capture_output=True,
        text=True
    )
    logger.debug(result.stdout)
    logger.error(result.stderr)
    if result.returncode == 0:
        logger.debug("✅ Photo taken successfully")
        return PlainTextResponse('📸 Photo taken.')
    else:
        logger.error("❌ Photo failed to execute")
        return PlainTextResponse('❌ Photo failed.', status_code=500)