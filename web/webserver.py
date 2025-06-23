from flask import Flask, send_file
import subprocess
from dotenv import set_key, load_dotenv
import os
import logging

load_dotenv('/home/ash/timelapse/config.env')
app = Flask(__name__)

# Log to file
logging.basicConfig(
    filename='/home/ash/timelapse/_local/webserver.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

@app.route('/')
def index():
    return send_file('/home/ash/timelapse/web/index.html')

@app.route('/style.css')
def style():
    return send_file('/home/ash/timelapse/web/style.css')

@app.route('/latest.jpg')
def latest():
    path = '/home/ash/timelapse/_local/latest.jpg'
    if not os.path.exists(path):
        return '', 404  # Clean fail instead of 500
    return send_file(path)

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
        return '❌ Photo failed.'

@app.route('/start')
def start():
    subprocess.run(['/home/ash/timelapse/run_all.sh'])
    return 'Capture process started.'

@app.route('/mode/wifi')
def switch_to_wifi():
    set_key('/home/ash/timelapse/config.env', 'wifi_mode', 'client')
    return 'Switched to Wi-Fi. Reboot or wait for next run_all.sh.'

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