# /home/ash/timelapse/interfaces/buttons/toggleHotWifi.py

import subprocess

with open("/home/ash/button_trigger.log", "a") as f:
    f.write("Button script was called\n")

def flash_led_script():
    subprocess.run(
        ["/usr/bin/python3", "/home/ash/timelapse/interfaces/buttons/flash_led.py"]
    )

flash_led_script()