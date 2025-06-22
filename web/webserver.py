from flask import Flask, send_file
import subprocess
from dotenv import set_key, load_dotenv
import os

load_dotenv('/home/ash/timelapse/config.env')
app = Flask(__name__)

@app.route('/')
def index():
    return send_file('web/index.html')

@app.route('/style.css')
def style():
    return send_file('web/style.css')

@app.route('/latest.jpg')
def latest():
    return send_file('/home/ash/timelapse/_local/latest.jpg')

@app.route('/photo')
def photo():
    subprocess.run(['python3', 'capture_test_photo.py'])
    return 'Test photo taken.'

@app.route('/start')
def start():
    subprocess.run(['/home/ash/timelapse/run_all.sh'])
    return 'Capture process started.'

@app.route('/mode/wifi')
def switch_to_wifi():
    set_key('/home/ash/timelapse/config.env', 'wifi_mode', 'client')
    return 'Switched to Wi-Fi. Reboot or wait for next run_all.sh.'