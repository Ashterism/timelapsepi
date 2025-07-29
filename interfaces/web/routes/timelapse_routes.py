from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import logging
from config.config_paths import SESSIONS_PATH
import datetime

from timelapse.sessionmgmt.session_manager import get_active_session
from timelapse.functions.start_timelapse import main_from_web
from timelapse.functions.stop_timelapse import main as stop_session
from timelapse.sessionmgmt.session_list import list_sessions

logger = logging.getLogger(__name__)
router = APIRouter()
timelapse_router = router

DEBUG_MODE = True

def debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

@router.post("/start")
async def start(request: Request):
    session = get_active_session()
    if session:
        return PlainTextResponse("❌ Session already running.", status_code=400)

    try:
        config_json = await request.json()
        from timelapse.functions.start_timelapse import debug
        debug(f"Config received in /start route: {config_json}")

        interval_str = config_json.get("interval", "")
        if not interval_str:
            return PlainTextResponse("❌ Interval is required.", status_code=400)
        h, m, s = map(int, interval_str.strip().split(":"))
        interval_seconds = h * 3600 + m * 60 + s

        folder_name = (config_json.get("folder") or "").strip()
        if not folder_name:
            folder_name = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S")
        folder_path = str(SESSIONS_PATH / folder_name)

        mode = config_json.get("end_type")
        if not mode:
            return PlainTextResponse("❌ End type is required.", status_code=400)

        config_dict = {
            "interval": interval_str,
            "start_time": config_json.get("start_time"),
            "folder": folder_name,
            "end_type": mode,
            "count": config_json.get("count"),
            "end_time": config_json.get("end_time")
        }

        if mode == "photo_count" and not config_dict["count"]:
            return PlainTextResponse("❌ Photo count required.", status_code=400)
        if mode == "end_time" and not config_dict["end_time"]:
            return PlainTextResponse("❌ End time required.", status_code=400)

        result = main_from_web(config_dict)
    except Exception as e:
        import traceback
        from timelapse.functions.start_timelapse import debug
        debug(f"❌ Exception in /start: {e}")
        debug(traceback.format_exc())
        return PlainTextResponse("💥 Server error. Check logs.", status_code=500)

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

