#!/usr/bin/env python3
from pijuice import PiJuice

pj = PiJuice(1, 0x14)
response = pj.config.GetUserFunction('USER_FUNC1')

if response['error'] == 'NO_ERROR':
    print("USER_FUNC1:", response['data'])
else:
    print("Error:", response['error'])
