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
battery_temp = pj.status.GetBatteryTemperature()
battery_voltage = pj.status.GetBatteryVoltage()
gpio_voltage_raw = pj.status.GetIoVoltage()
gpio_current_raw = pj.status.GetIoCurrent()

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

def get_throttling():
    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode()
        return output.strip().split("=")[1]
    except:
        return "Unavailable"

# Convert GPIO voltage/current to V/A
gpio_voltage_V = gpio_voltage_raw.get("data", 0) / 1000 if isinstance(gpio_voltage_raw.get("data"), (int, float)) else "Unavailable"
gpio_current_A = gpio_current_raw.get("data", 0) / 1000 if isinstance(gpio_current_raw.get("data"), (int, float)) else "Unavailable"

# Build log
log = {
    "timestamp": datetime.now().isoformat(),
    "battery_level": charge.get("data", "N/A"),
    "battery_temp_C": battery_temp.get("data", "N/A"),
    "battery_voltage_mV": battery_voltage.get("data", "N/A"),
    "gpio_voltage_V": gpio_voltage_V,
    "gpio_current_A": gpio_current_A,
    "power_input_usb": status.get("data", {}).get("powerInput", "Unknown"),
    "power_input_gpio": status.get("data", {}).get("powerInput5vIo", "Unknown"),
    "power_status": status.get("data", {}).get("battery", "Unknown"),
    "cpu_temp_C": get_cpu_temp(),
    "cpu_load": get_load_avg(),
    "uptime_s": get_uptime(),
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
