#!/usr/bin/env python3

from datetime import datetime
from time import sleep
from pijuice import PiJuice

LOG_PATH = "/home/ash/timelapse/_local/button_test.log"
pj = PiJuice(1, 0x14)

# Log it
with open(LOG_PATH, "a") as f:
    f.write(f"{datetime.now()}: Button triggered!\n")

# Flash LED (teal then off, once)
pj.status.SetLedBlink('D2', 1, [0, 200, 100], 300, [0, 0, 0], 300)
sleep(0.6)