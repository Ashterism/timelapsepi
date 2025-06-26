#!/usr/bin/env python3

from datetime import datetime
from time import sleep
from pijuice import PiJuice
from config.config_paths import BUTTON_TRIGGER_LOG

LOG_PATH = BUTTON_TRIGGER_LOG
pj = PiJuice(1, 0x14)

# Log it
with open(LOG_PATH, "a") as f:
    f.write(f"{datetime.now()}: Button triggered!\n")

# Flash LED (teal then off, once)
pj.status.SetLedBlink('D2', 1, [0, 200, 100], 300, [0, 0, 0], 300)
sleep(0.6)