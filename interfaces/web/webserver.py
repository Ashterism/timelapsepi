from flask import Flask, send_file, jsonify, request
import subprocess
from dotenv import set_key, load_dotenv
import os
import logging
from config.config_paths import CONFIG_PATH, LOGS_PATH, INTERFACES_PATH, PHOTO_SCRIPT, TEMP_PATH
from timelapse.sessionmgt.session_manager import get_active_session
from timelapse.sessionmgt.session_list import list_sessions

load_dotenv(CONFIG_PATH)
app = Flask(__name__)

# Log to file
logging.basicConfig(
    filename = LOGS_PATH / "webserver.log",
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

@app.before_request
def log_request_info():
    app.logger.info(f"🔹 Incoming request: {request.method} {request.path}")

@app.route('/')
def index():
    return send_file(INTERFACES_PATH / "web" / "index.html")

@app.route('/style.css')
def style():
    return send_file(INTERFACES_PATH / "web" / "style.css")

@app.route('/photo.js')
def photo_js():
    return send_file(INTERFACES_PATH / "web" / "photo.js")

@app.route('/latest.jpg')
def latest():
    path = TEMP_PATH / "latest.jpg"
    if not os.path.exists(path):
        return '', 404
    return send_file(path)

@app.route('/latest-timestamp')
def latest_timestamp():
    path = TEMP_PATH / "latest.json"
    if not os.path.exists(path):
        return '', 404
    try:
        import json
        with open(path) as f:
            data = json.load(f)
        return data.get("timestamp", ""), 200
    except Exception as e:
        app.logger.error(f"Error reading latest.json: {e}")
        return '', 500


@app.route('/photo')
def photo():
    app.logger.debug("📸 /photo route hit")

    # Prevent photo if a session is active
    session = get_active_session()
    if session:
        app.logger.warning("❌ Cannot take test photo: session is active.")
        return '❌ Session in progress. Stop it before taking a test photo.', 400

    result = subprocess.run(
        ['/bin/bash', str(PHOTO_SCRIPT)],
        capture_output=True,
        text=True
    )
    app.logger.debug(result.stdout)
    app.logger.error(result.stderr)
    if result.returncode == 0:
        app.logger.debug("✅ Photo taken successfully")
        return '📸 Photo taken.'
    else:
        app.logger.error("❌ Photo failed to execute")
        return '❌ Photo failed.', 500

@app.route('/health')
def health():
    try:
        with open(TEMP_PATH / "latest.jpg", 'rb') as f:
            pass
        return 'OK', 200
    except:
        return 'File error', 500

@app.route('/webserverlog')
def show_log():
    try:
        with open(LOGS_PATH / "webserver.log", 'r') as f:
            lines = f.readlines()[-50:]
        return '<pre>' + ''.join(lines) + '</pre>'
    except FileNotFoundError:
        return '⚠️ Log file not found'

@app.route('/mode/wifi')
def switch_to_wifi():
    set_key(CONFIG_PATH, 'wifi_mode', 'client')
    return 'Switched to Wi-Fi. Reboot or wait for next tma1.sh.'

@app.route('/status')
def status():
    try:
        uptime = subprocess.check_output(['uptime', '-p']).decode().strip()
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
        mode = os.getenv('wifi_mode', 'unknown')

        # Session management
        session = get_active_session()
        session_info = f"<br>📂 Session: {session}" if session else "<br>📂 Session: None"

        return f"🟢 Status OK<br>Uptime: {uptime}<br>IP: {ip}<br>Mode: {mode}{session_info}"
    except Exception as e:
        return f"🔴 Status error: {str(e)}"

@app.route('/start')
def start_timelapse():
    session = get_active_session()
    if session:
        app.logger.warning("❌ Cannot start new session: one is already active.")
        return '❌ Session already running. Stop it first.', 400

    try:
        result = subprocess.run(
            ['python3', str(INTERFACES_PATH / "start_timelapse.py")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            app.logger.info("✅ Session started via web.")
            return '✅ Timelapse started.', 200
        else:
            app.logger.error(f"❌ Timelapse start failed:\n{result.stderr}")
            return '❌ Timelapse start failed.', 500
    except Exception as e:
        app.logger.error(f"❌ Exception starting timelapse: {e}")
        return f"❌ Exception: {str(e)}", 500

@app.route('/stop')
def stop_timelapse():
    try:
        result = subprocess.run(
            ['python3', str(INTERFACES_PATH / "stop_timelapse.py")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            app.logger.info("🛑 Timelapse stopped via web.")
            return '🛑 Timelapse stopped.', 200
        else:
            app.logger.error(f"❌ Stop failed:\n{result.stderr}")
            return '❌ Stop failed.', 500
    except Exception as e:
        app.logger.error(f"❌ Exception stopping timelapse: {e}")
        return f"❌ Exception: {str(e)}", 500


# Route to list sessions
@app.route('/sessions')
def sessions():
    try:
        sessions = list_sessions()
        html = "<h2>📂 Timelapse Sessions</h2><ul>"
        for s in sessions:
            flag = "🟢" if s["is_active"] else "⚪"
            html += f"<li>{flag} {s['path']}</li>"
        html += "</ul>"
        return html
    except Exception as e:
        app.logger.error(f"❌ Failed to load sessions: {e}")
        return f"❌ Error loading sessions: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)