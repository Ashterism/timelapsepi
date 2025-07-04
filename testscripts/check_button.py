#!/usr/bin/env python3

from pijuice import PiJuice

pj = PiJuice(1, 0x14)
response = pj.config.GetButtonConfiguration('SW1')

if response['error'] == 'NO_ERROR':
    print("Button config:", response['data'])
else:
    print("Error:", response['error'])
