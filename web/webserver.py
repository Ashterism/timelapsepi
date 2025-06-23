from flask import Flask, send_file
import subprocess
from dotenv import set_key, load_dotenv
import os

load_dotenv('/home/ash/timelapse/config.env')
app = Flask(__name__)

@app.route('/')
def index():
    return send_file('/home/ash/timelapse/web/index.html')

@app.route('/style.css')
def style():
    return send_file('/home/ash/timelapse/web/style.css')

@app.route('/latest.jpg')
def latest():
    return send_file('/home/ash/timelapse/_local/latest.jpg')

@app.route('/photo')
def photo():
    result = subprocess.run('source /home/ash/timelapse/functions/photo.sh && take_photo', shell=True)
    return '📸 Photo taken.' if result.returncode == 0 else '❌ Photo failed.'

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