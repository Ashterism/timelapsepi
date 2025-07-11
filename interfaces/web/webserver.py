
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from dotenv import set_key, load_dotenv
import subprocess
import logging
import json
import os

from config.config_paths import CONFIG_PATH, LOGS_PATH, INTERFACES_PATH, PHOTO_SCRIPT, TEMP_PATH
from timelapse.sessionmgmt.session_manager import get_active_session
from timelapse.sessionmgmt.session_list import list_sessions

load_dotenv(CONFIG_PATH)
app = FastAPI()

# Log to file
logging.basicConfig(
    filename=LOGS_PATH / "webserver.log",
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🔹 Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/")
def index():
    return FileResponse(INTERFACES_PATH / "web" / "index.html")

@app.get("/style.css")
def style():
    return FileResponse(INTERFACES_PATH / "web" / "style.css")

@app.get("/photo.js")
def photo_js():
    return FileResponse(INTERFACES_PATH / "web" / "photo.js")

@app.get("/latest.jpg")
def latest_jpg():
    path = TEMP_PATH / "latest.jpg"
    if not os.path.exists(path):
        return PlainTextResponse('', status_code=404)
    return FileResponse(path)

@app.get("/latest-timestamp")
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

@app.post("/photo")
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

@app.get("/health")
def health():
    try:
        with open(TEMP_PATH / "latest.jpg", 'rb'):
            return PlainTextResponse("OK")
    except:
        return PlainTextResponse("File error", status_code=500)

@app.get("/webserverlog")
def show_log():
    try:
        with open(LOGS_PATH / "webserver.log", 'r') as f:
            lines = f.readlines()[-50:]
        return HTMLResponse('<pre>' + ''.join(lines) + '</pre>')
    except FileNotFoundError:
        return PlainTextResponse('⚠️ Log file not found')

@app.get("/mode/wifi")
def switch_to_wifi():
    set_key(CONFIG_PATH, 'wifi_mode', 'client')
    return PlainTextResponse('Switched to Wi-Fi. Reboot or wait for next tma1.sh.')

@app.get("/status")
def status():
    try:
        uptime = subprocess.check_output(['uptime', '-p']).decode().strip()
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
        mode = os.getenv('wifi_mode', 'unknown')
        session = get_active_session()
        session_info = f"<br>📂 Session: {session}" if session else "<br>📂 Session: None"
        return HTMLResponse(f"🟢 Status OK<br>Uptime: {uptime}<br>IP: {ip}<br>Mode: {mode}{session_info}")
    except Exception as e:
        return PlainTextResponse(f"🔴 Status error: {str(e)}")

@app.post("/start")
def start_timelapse():
    session = get_active_session()
    if session:
        logger.warning("❌ Cannot start new session: one is already active.")
        return PlainTextResponse('❌ Session already running. Stop it first.', status_code=400)
    try:
        result = subprocess.run(
            ['python3', str(INTERFACES_PATH / "start_timelapse.py")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("✅ Session started via web.")
            return PlainTextResponse('✅ Timelapse started.')
        else:
            logger.error(f"❌ Timelapse start failed:\n{result.stderr}")
            return PlainTextResponse('❌ Timelapse start failed.', status_code=500)
    except Exception as e:
        logger.error(f"❌ Exception starting timelapse: {e}")
        return PlainTextResponse(f"❌ Exception: {str(e)}", status_code=500)

@app.post("/stop")
def stop_timelapse():
    try:
        result = subprocess.run(
            ['python3', str(INTERFACES_PATH / "stop_timelapse.py")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("🛑 Timelapse stopped via web.")
            return PlainTextResponse('🛑 Timelapse stopped.')
        else:
            logger.error(f"❌ Stop failed:\n{result.stderr}")
            return PlainTextResponse('❌ Stop failed.', status_code=500)
    except Exception as e:
        logger.error(f"❌ Exception stopping timelapse: {e}")
        return PlainTextResponse(f"❌ Exception: {str(e)}", status_code=500)

@app.get("/sessions")
def sessions():
    try:
        sessions = list_sessions()
        html = "<h2>📂 Timelapse Sessions</h2><ul>"
        for s in sessions:
            flag = "🟢" if s["is_active"] else "⚪"
            html += f"<li>{flag} {s['path']}</li>"
        html += "</ul>"
        return HTMLResponse(html)
    except Exception as e:
        logger.error(f"❌ Failed to load sessions: {e}")
        return PlainTextResponse(f"❌ Error loading sessions: {str(e)}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("interfaces.web.webserver:app", host="0.0.0.0", port=5000, reload=False)