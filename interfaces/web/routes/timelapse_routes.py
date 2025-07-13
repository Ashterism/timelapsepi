from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import logging

from timelapse.sessionmgmt.session_manager import get_active_session
from timelapse.functions.start_timelapse import start_session_from_config
from timelapse.functions.stop_timelapse import main as stop_session
from timelapse.sessionmgmt.session_list import list_sessions

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start")
async def start(request: Request):
    session = get_active_session()
    if session:
        return PlainTextResponse("❌ Session already running.", status_code=400)

    config = await request.json()
    try:
        result = start_session_from_config(config)
    except Exception as e:
        logger.error(f"Failed to start session from config: {e}")
        return PlainTextResponse("❌ Failed to start session.", status_code=500)

    if result:
        return PlainTextResponse("🚀 Session started.")
    return PlainTextResponse("❌ Failed to start session.", status_code=500)

@router.post("/stop")
def stop():
    session = get_active_session()
    if not session:
        return PlainTextResponse("⚠️ No session to stop.", status_code=400)
    result = stop_session()
    if result:
        return PlainTextResponse("🛑 Session stopped.")
    return PlainTextResponse("❌ Failed to stop session.", status_code=500)

@router.get("/sessions")
def sessions():
    return list_sessions()