#!/usr/bin/env python3

import time
from pijuice import PiJuice

pj = PiJuice(1, 0x14)

print("📟 Waiting for PiJuice button events (press Ctrl+C to exit)...")
pj.status.SetButtonEvents({'SW1': {}})  # Manually clear existing events

while True:
    event = pj.status.GetButtonEvents()
    if event['error'] == 'NO_ERROR' and event['data']:
        print(f"🟢 Button event detected: {event['data']}")
        pj.status.SetButtonEvents({'SW1': {}})  # Clear again after each event
    time.sleep(0.2)
