import time
from pijuice import PiJuice

pj = PiJuice(1, 0x14)

print("📟 Waiting for PiJuice button events (press Ctrl+C to exit)...")

pj.status.ResetButtonEvents()

while True:
    event = pj.status.GetButtonEvents()
    if event['error'] == 'NO_ERROR' and event['data']:
        print(f"🟢 Button event detected: {event['data']}")
        pj.status.ResetButtonEvents()
    time.sleep(0.2)
