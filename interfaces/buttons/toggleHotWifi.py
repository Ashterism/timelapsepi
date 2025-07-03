# /home/ash/timelapse/interfaces/buttons/toggleHotWifi.py

import subprocess

def flash_led_script():
    subprocess.run(
        ["/usr/bin/python3", "/home/ash/timelapse/interfaces/buttons/flash_led.py"]
    )

flash_led_script()