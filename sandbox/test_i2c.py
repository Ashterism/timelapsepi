from config.config_paths import CONFIG_PATH
from dotenv import load_dotenv
load_dotenv(CONFIG_PATH)
from smbus2 import SMBus

bus = SMBus(1)
address = 0x14  # PiJuice I2C address

try:
    value = bus.read_byte_data(address, 0x00)
    print(f"Read byte: {value}")
except Exception as e:
    print(f"Error reading from PiJuice: {e}")
