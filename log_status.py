from pijuice import PiJuice
from datetime import datetime
import os

pj = PiJuice(1, 0x14)  # Explicitly define bus and address

status = pj.status.GetStatus()
charge = pj.status.GetChargeLevel()

print("STATUS:", status)
print("CHARGE:", charge)

log = {
    "timestamp": datetime.now().isoformat(),
    "battery_level": charge.get("data", "N/A"),
    "power_input": status.get("data", {}).get("powerInput", "Unknown"),
    "power_status": status.get("data", {}).get("powerStatus", "Unknown"),
    "temperature_C": status.get("data", {}).get("batteryTemperature", "Unknown")
}

with open(os.path.expanduser("~/timelapse/status.json"), "w") as f:
    f.write(str(log))

