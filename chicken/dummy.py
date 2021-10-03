# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: dummy.py

Dummy classes for the hardware devices on the Chicken Pi (for testing)

"""

# Built-In Libraries

# 3rd Party Libraries

# Internal Imports


def set_up_sensors():
    """set_up_sensors Set up the dummy sensors for testing on Mac

    Returns
    -------
    `dict`
        A dictionary containing the dummy sensors
    """
    # Use a dictionary for holding the sensor instances
    sensors = {}

    # Inside the Pi box -- AHT10 temp/humid sensor to monitor conditions
    sensors['box'] = DummyTH()

    # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
    sensors['inside'] = DummyTH()

    # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
    sensors['outside'] = DummyTH()

    # Outside the coop -- TSL2591 light sensor
    sensors['light'] = DummyLux()

    return sensors


#=========================================================#
# Dummy Sensors for testing of the code NOT on a RPi
class DummyTH:
    """ Dummy Temp/Humid Sensor Class

    Includes dummy values for testing
    """
    def __init__(self):
        self.temp = 74.2
        self.humid = 42.3
        self.cache_temp = 75.6
        self.cache_humid = 99.0
        self.data_entry = (self.cache_temp, self.cache_humid)


class DummyLux:
    """ Dummy Lux Sensor Class

    Includes dummy values for testing
    """
    def __init__(self):
        self.level = 502
        self.cache_level = 6521
        self.data_entry = (self.cache_level)


class Relay:
    """ Dummy Relay Class

    [extended_summary]
    """
    _WRITE_BUF = bytearray(5)
    def __init__(self):
        self.state = [False] * 4

    def write(self):
        """write Write out something?

        [extended_summary]
        """
        self._WRITE_BUF[0] = 0x01
        for i, relay in enumerate(self.state, 1):
            self._WRITE_BUF[i] = 0xff if relay else 0x00
