from flask import Flask, send_file, jsonify
import subprocess
from dotenv import set_key, load_dotenv
import os
import logging

load_dotenv('/home/ash/timelapse/operations/config.env')
app = Flask(__name__)

# Log to file
logging.basicConfig(
    filename = '/home/ash/timelapse/data/logs/webserver.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

@app.route('/')
def index():
    return send_file('/home/ash/timelapse/interfaces/web/index.html')

@app.route('/style.css')
def style():
    return send_file('/home/ash/timelapse/interfaces/web/style.css')

@app.route('/photo.js')
def photo_js():
    return send_file('/home/ash/timelapse/interfaces/web/photo.js')

@app.route('/latest.jpg')
def latest():
    path = '/home/ash/timelapse/data/temp/latest.jpg'
    if not os.path.exists(path):
        return '', 404  # Clean fail instead of 500
    return send_file(path)

@app.route('/latest-timestamp')
def latest_timestamp():
    path = '/home/ash/timelapse/data/temp/latest.jpg'
    if not os.path.exists(path):
        return '', 404
    timestamp = str(os.path.getmtime(path))
    return timestamp

@app.route('/photo')
def photo():
    app.logger.debug("📸 /photo route hit")
    result = subprocess.run(
        ['/bin/bash', '/home/ash/timelapse/functions/photo.sh'],
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

@app.route('/webserverlog')
def show_log():
    try:
        with open('/home/ash/timelapse/logs/webserver.log', 'r') as f:
            lines = f.readlines()[-50:]  # Show last 50 lines
        return '<pre>' + ''.join(lines) + '</pre>'
    except FileNotFoundError:
        return '⚠️ Log file not found'

@app.route('/mode/wifi')
def switch_to_wifi():
    set_key('/home/ash/timelapse/operations/config.env', 'wifi_mode', 'client')
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