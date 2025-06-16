from pijuice import PiJuice
from datetime import datetime
import os
import json

pj = PiJuice(1, 0x14)  # Explicitly define bus and address

status = pj.status.GetStatus()
charge = pj.status.GetChargeLevel()

print("STATUS:", status)
print("CHARGE:", charge)

power_input = status.get("data", {}).get("powerInput", "Unknown")
raw_power_status = status.get("data", {}).get("powerStatus")
power_status = raw_power_status if raw_power_status else "Not managed by PiJuice"
temperature = status.get("data", {}).get("batteryTemperature", "Unknown")

log = {
    "timestamp": datetime.now().isoformat(),
    "battery_level": charge.get("data", "N/A"),
    "power_input": power_input,
    "power_status": power_status,
    "temperature_C": temperature
}

with open(os.path.expanduser("~/timelapse/status.json"), "w") as f:
    f.write(json.dumps(log, indent=2))
