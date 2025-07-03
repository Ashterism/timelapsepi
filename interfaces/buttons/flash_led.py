# flash_led.py

from pijuice import PiJuice
import time

pj = PiJuice(1, 0x14)  # I2C bus 1, default PiJuice address

def flash_led(times=3, on_time=0.3, off_time=0.3):
    for _ in range(times):
        pj.config.SetLedState('D1', 'ON')
        time.sleep(on_time)
        pj.config.SetLedState('D1', 'OFF')
        time.sleep(off_time)

if __name__ == "__main__":
    flash_led()