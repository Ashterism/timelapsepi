from pijuice import PiJuice
import time

pj = PiJuice(1, 0x14)  # I2C bus 1, default PiJuice address

def flash_led():
    pj.status.SetLedBlink('D2', 1, [0, 200, 100], 300, [0, 0, 0], 300)
    time.sleep(0.6)  # Wait for blink to complete

if __name__ == "__main__":
    flash_led()