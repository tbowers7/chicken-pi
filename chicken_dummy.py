# -*- coding: utf-8 -*-

"""
  FILE: chicken_devices.py

Control classes for the hardware devices on the Chicken Pi

"""

# Built-in/Generic Imports
# […]

# Libs

# Hardware Libs

# Own modules
#from {path} import {class}


def set_up_sensors():

    # Use a dictionary for holding the sensor instances
    sensors = {}

    # Inside the Pi box -- AHT10 temp/humid sensor to monitor conditions
    sensors['box'] = DummySensor()

    # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
    sensors['inside'] = DummySensor()

    # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
    sensors['outside'] = DummySensor()

    # Outside the coop -- TSL2591 light sensor
    sensors['light'] = DummySensor()

    return sensors




#=========================================================#
# Dummy Sensors for testing of the code NOT on a RPi

class DummySensor:
    def __init__(self):
        self.temp = 74.2
        self.humid = 42.3
        self.lux = 502

class Relay:
    _WRITE_BUF = bytearray(5)
    def __init__(self):
        self.state = [False] * 4
    def write(self):
        self._WRITE_BUF[0] = 0x01
        for i, r in enumerate(self.state, 1):
            self._WRITE_BUF[i] = 0xff if r else 0x00
