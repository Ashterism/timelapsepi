from flask import Flask, send_file, jsonify, request
import subprocess
from dotenv import set_key, load_dotenv
import os
import logging
from config.config_paths import CONFIG_PATH, LOGS_PATH, INTERFACES_PATH, PHOTO_SCRIPT, TEMP_PATH

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
    path = TEMP_PATH / "latest.jpg"
    if not os.path.exists(path):
        return '', 404
    timestamp = str(os.path.getmtime(path))
    return timestamp

@app.route('/photo')
def photo():
    app.logger.debug("📸 /photo route hit")
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
        return f"🟢 Status OK<br>Uptime: {uptime}<br>IP: {ip}<br>Mode: {mode}"
    except Exception as e:
        return f"🔴 Status error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)