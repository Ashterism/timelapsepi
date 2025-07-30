from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from dotenv import set_key, load_dotenv
import subprocess
import logging
import json
import os

from config.config_paths import CONFIG_PATH, LOGS_PATH, INTERFACES_PATH, TEMP_PATH
from timelapse.sessionmgmt.session_manager import get_active_session
from timelapse.sessionmgmt.session_list import list_sessions
load_dotenv(CONFIG_PATH)
app = FastAPI()

from interfaces.web.routes.photo_routes import router as photo_router
from interfaces.web.routes.timelapse_routes import timelapse_router
from interfaces.web.routes.session_routes import router as session_router
app.include_router(photo_router, prefix="")
app.include_router(timelapse_router)
app.include_router(session_router)

# Add status_router after timelapse_router
from interfaces.web.routes.status_route import router as status_router
app.include_router(status_router)

app.mount("/static", StaticFiles(directory=INTERFACES_PATH / "web" / "static"), name="static")

# Mount sessions static directory
from config.config_paths import SESSIONS_PATH

app.mount(
    "/sessions",
    StaticFiles(directory=SESSIONS_PATH),
    name="sessions"
)

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

@app.get("/debug-path")
def debug_path():
    return PlainTextResponse(str(INTERFACES_PATH / "web" / "static" / "scripts.js"))


@app.get("/health")
def health():
    return PlainTextResponse("OK")
    

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


# JSON status endpoint
@app.get("/status/json")
def status_json():
    try:
        uptime = subprocess.check_output(['uptime', '-p']).decode().strip()
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
        mode = os.getenv('wifi_mode', 'unknown')
        battery = os.getenv('battery_level', 'N/A')  # Placeholder, replace with real logic if available
        return {
            "uptime": uptime,
            "ip": ip,
            "connection": mode,
            "battery": battery
        }
    except Exception as e:
        return {"error": str(e)}

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

# Test route to check if root is working
@app.get("/test-root")
def test_root():
    print("test-root route called")
    return {"message": "Root test route is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("interfaces.web.webserver:app", host="0.0.0.0", port=5000, reload=False)
