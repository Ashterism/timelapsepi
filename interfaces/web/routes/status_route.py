

from fastapi import APIRouter
import subprocess
import os
import json
from pijuice import PiJuice

router = APIRouter()

def get_battery_info():
    try:
        pj = PiJuice(1, 0x14)
        status = pj.status.GetChargeLevel()
        if status['error'] == 'NO_ERROR':
            return {
                "level": status['data'],
                "charging": pj.status.GetStatus()['data']['powerInput'] != "NOT_PRESENT"
            }
        else:
            return {"level": None, "charging": None}
    except Exception:
        return {"level": None, "charging": None}

def get_connection_info():
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
        mode = os.getenv('wifi_mode', 'unknown')
        return {"ip": ip, "mode": mode}
    except Exception:
        return {"ip": None, "mode": "unknown"}

@router.get("/status")
def status():
    return {
        "battery": get_battery_info(),
        "connection": get_connection_info()
    }