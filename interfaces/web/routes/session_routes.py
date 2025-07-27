from fastapi import APIRouter
from fastapi import Query
from pathlib import Path
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