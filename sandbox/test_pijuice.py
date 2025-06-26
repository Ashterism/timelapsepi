from config.config_paths import CONFIG_PATH
from dotenv import load_dotenv
load_dotenv(CONFIG_PATH)
from pijuice import PiJuice

pj = PiJuice(1, 0x14)  # bus 1, default address

try:
    status = pj.status.GetStatus()
    print("STATUS:", status)
except Exception as e:
    print("Error:", e)
