#!/usr/bin/python3

# /home/ash/timelapse/interfaces/buttons/button_run.py

import subprocess

def call_script(script_path):
    subprocess.run(["/usr/bin/python3", script_path])

if __name__ == "__main__":
    call_script("/home/ash/timelapse/interfaces/buttons/flash_led.py")