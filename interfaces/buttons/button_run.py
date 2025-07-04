#!/usr/bin/python3

# /home/ash/timelapse/interfaces/buttons/button_run.py

import subprocess

def call_script(script_path):
    if script_path.endswith(".py"):
        subprocess.run(["/usr/bin/python3", script_path])
    elif script_path.endswith(".sh"):
        subprocess.run(["/bin/bash", script_path])

if __name__ == "__main__":
    call_script("/home/ash/timelapse/interfaces/buttons/flash_led.py")
    call_script("/home/ash/timelapse/operations/ssh_watchdog.sh")