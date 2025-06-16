from pijuice import PiJuice
from datetime import datetime
import os
import json
import subprocess

# Set log location
log_dir = "/home/ash/timelapse/_local/logs"
os.makedirs(log_dir, exist_ok=True)

# Setup PiJuice
pj = PiJuice(1, 0x14)
status = pj.status.GetStatus()
charge = pj.status.GetChargeLevel()

# Extract data
power_input = status.get("data", {}).get("powerInput", "Unknown")
raw_power_status = status.get("data", {}).get("powerStatus")
power_status = raw_power_status if raw_power_status else "Not managed by PiJuice"
battery_temp = status.get("data", {}).get("batteryTemperature", "Unknown")
battery_level = charge.get("data", "N/A")

# Raspberry Pi system stats
def get_cpu_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return float(output.replace("temp=", "").replace("'C\n", ""))
    except:
        return "Unavailable"

def get_load_avg():
    try:
        with open("/proc/loadavg", "r") as f:
            return f.read().strip().split()[:3]
    except:
        return ["-", "-", "-"]

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            return int(uptime_seconds)
    except:
        return "Unavailable"
    
def format_uptime(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    return f"{days}d {hours % 24}h {minutes % 60}m"

def get_throttling():
    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode()
        return output.strip().split("=")[1]
    except:
        return "Unavailable"
    
# Get uptime once
uptime = get_uptime()

#Build log
log = {
    "timestamp": datetime.now().isoformat(),
    "battery_level": battery_level,
    "power_input": power_input,
    "power_input_gpio": status.get("data", {}).get("gpioPowerInput", "Unavailable"),
    "power_input_usb": status.get("data", {}).get("usbPowerInput", "Unavailable"),
    "power_status": power_status,
    "temperature_C": battery_temp,
    "cpu_temp_C": get_cpu_temp(),
    "cpu_load": get_load_avg(),
    "uptime_s": uptime,
    "uptime_str": format_uptime(uptime) if isinstance(uptime, int) else "Unavailable",
    "throttled": get_throttling()
}

# Save to timestamped file
timestamp = log["timestamp"]
log_filename = f"{log_dir}/{timestamp}.json"
with open(log_filename, "w") as f:
    json.dump(log, f, indent=2)

# Also save current status.json for debugging
with open("/home/ash/timelapse/status.json", "w") as f:
    json.dump(log, f, indent=2)