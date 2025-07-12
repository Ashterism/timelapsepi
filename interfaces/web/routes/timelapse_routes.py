from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import logging

from timelapse.sessionmgmt.session_manager import get_active_session
## from timelapse.functions.start_timelapse import start_session
## from timelapse.functions.stop_timelapse import stop_session
from timelapse.sessionmgmt.session_list import list_sessions

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/photo")

## @router.post("/start")
## def start():
##     session = get_active_session()
##     if session:
##         return PlainTextResponse("❌ Session already running.", status_code=400)
##     result = start_session()
##     if result:
##         return PlainTextResponse("🚀 Session started.")
##     return PlainTextResponse("❌ Failed to start session.", status_code=500)

## @router.post("/stop")
## def stop():
##     session = get_active_session()
##     if not session:
##         return PlainTextResponse("⚠️ No session to stop.", status_code=400)
##     result = stop_session()
##     if result:
##         return PlainTextResponse("🛑 Session stopped.")
##     return PlainTextResponse("❌ Failed to stop session.", status_code=500)

@router.get("/sessions")
def sessions():
    return list_sessions()