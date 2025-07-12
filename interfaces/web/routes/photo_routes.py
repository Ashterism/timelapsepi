from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import os
import json
import logging

from config.config_paths import INTERFACES_PATH, TEMP_PATH
from timelapse.functions.take_photo import take_photo
from timelapse.sessionmgmt.session_manager import get_active_session

logger = logging.getLogger(__name__)
router = APIRouter()

logger.debug("✅ photo_routes.py router loaded")

@router.get("/latest.jpg")
def latest_jpg():
    path = TEMP_PATH / "latestjpg" / "latest.jpg"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    return FileResponse(path)

@router.get("/latest-timestamp")
def latest_timestamp():
    path = TEMP_PATH / "latestjpg" / "latest.json"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    try:
        with open(path) as f:
            data = json.load(f)
        return PlainTextResponse(data.get("timestamp", ""), status_code=200)
    except Exception as e:
        logger.error(f"Error reading latest.json: {e}")
        return PlainTextResponse('', status_code=500)
    
@router.get("/latest.json")
def latest_json():
    path = TEMP_PATH / "latestjpg" / "latest.json"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    try:
        with open(path) as f:
            data = json.load(f)
        return data
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

    success = take_photo()
    if success:
        logger.debug("✅ Photo taken successfully")
        return PlainTextResponse('📸 Photo taken.')
    else:
        logger.error("❌ Photo failed to execute")
        return PlainTextResponse('❌ Photo failed.', status_code=500)