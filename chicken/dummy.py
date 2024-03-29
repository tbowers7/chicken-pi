# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: dummy.py

Dummy classes for the hardware devices on the Chicken Pi (for testing)

"""

# Built-In Libraries

# 3rd Party Libraries

# Internal Imports


def set_up_sensors():
    """Set up the dummy sensors for testing on Mac

    Returns
    -------
    sensors : dict
        A dictionary containing the dummy sensors
    relays : :class:`Relay`
        The dummy relay class
    """
    return {
        # Inside the Pi box -- AHT10 temp/humid sensor on I2C bus #1
        "box": DummyTH(),
        # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
        "inside": DummyTH(),
        # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
        "outside": DummyTH(),
        # Outside the coop -- TSL2591 light sensor on I2C bus #3
        "light": DummyLux(),
        # Raspberry Pi CPU
        "cpu": DummyCPU(),
    }, Relay


# =========================================================#
# Dummy Sensors for testing of the code NOT on a RPi
class DummyTH:
    """Dummy Temp/Humid Sensor Class

    Includes dummy values for testing
    """

    def __init__(self):
        self.temp = 74.2
        self.humid = 42.3
        self.cache_temp = 75.6
        self.cache_humid = 99.0
        self.data_entry = (self.cache_temp, self.cache_humid)


class DummyLux:
    """Dummy Lux Sensor Class

    Includes dummy values for testing
    """

    def __init__(self):
        self.level = 502
        self.cache_level = 6521
        self.data_entry = self.cache_level


class DummyCPU:
    """Dummy RPi CPU Class

    Includes dummy values for testing
    """

    def __init__(self):
        self.temp = -99
        self.cache_temp = -99
        self.data_entry = self.cache_temp


class Old3ARelay:
    """Dummy Relay Class

    [extended_summary]
    """

    _WRITE_BUF = bytearray(5)

    def __init__(self):
        # Make instance variable, and write 0's to relay HAT
        self.good_write = None
        self.state = [False] * 4
        self.write()

    def write(self):
        """Write out something?

        [extended_summary]
        """
        self._WRITE_BUF[0] = 0x01
        for i, relay in enumerate(self.state, 1):
            self._WRITE_BUF[i] = 0xFF if relay else 0x00
        self.good_write = True


class Relay(Old3ARelay):
    """Placeholder while I'm working to move to the KS0212 relay board

    _extended_summary_
    """
