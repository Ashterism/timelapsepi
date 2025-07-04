#!/usr/bin/env python3
from datetime import datetime
with open("/home/ash/button_debug.log", "a") as f:
    f.write(f"[{datetime.now().isoformat()}] SW1 pressed!\n")
