#!/usr-bin/env python3

from pijuice import PiJuice
import time

pj = PiJuice(1, 0x14)  # I2C bus 1, default PiJuice address

def flash_led():
    # SetLedBlink(led, count, rgb1, period1, rgb2, period2)
    # Flash LED D2 twice in teal colour (RGB 0,200,100) for 300ms on, 300ms off.
    # To change colour, adjust rgb1; to change duration, adjust period1/period2 (in ms).
    pj.status.SetLedBlink('D2', 2, [0, 200, 100], 300, [0, 0, 0], 300)
    time.sleep(0.6)  # Wait for blink to complete

if __name__ == "__main__":
    flash_led()


