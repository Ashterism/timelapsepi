#!/usr/bin/env python3

from datetime import datetime
import os

LOG_PATH = "/home/ash/timelapse/_local/button_test.log"
LED_CMD = "/usr/bin/pijuice_cli led blink blue 3"

# Log it
with open(LOG_PATH, "a") as f:
    f.write(f"{datetime.now()}: Button triggered!\n")

# Flash the LED
os.system(LED_CMD)