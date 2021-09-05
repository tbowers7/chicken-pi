# -*- coding: utf-8 -*-

"""
  FILE: chicken_devices.py

Control classes for the hardware devices on the Chicken Pi

"""

# Futures
# […]

# Built-in/Generic Imports
import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const
# […]

# Libs
import numpy as np         # Numpy!

# Hardware Libs
import adafruit_tsl2591                 # Outside light sensor
import adafruit_sht31d                  # Inside/outside temp/humid sensors (x2)
import adafruit_ahtx0                   # Internal (box) temp/humid sensor
from adafruit_motorkit import MotorKit  # Motor HAT

# Own modules
#from {path} import {class}

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2021, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.2.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 3 - Alpha'

# Internal constants:
_RELAY_ADDR        = const(0x10)
_RELAY_COMMAND_BIT = const(0x01)


# implementation of the TSL2591 for the chicken-pi
class TSL2591:

    def __init__(self):
        # Initialize the I2C bus.
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize the sensor.
        try:
            self.sensor = adafruit_tsl2591.TSL2591(self.i2c)
        except ValueError:
            self.sensor = None
        
        self.goodRead = 0

    # Define functions to increase or decrease the gain
    def decrease_gain(sensor):
        if sensor.gain == adafruit_tsl2591.GAIN_MAX:
            sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            sensor.gain = adafruit_tsl2591.GAIN_MED
        elif sensor.gain == adafruit_tsl2591.GAIN_MED:
            sensor.gain = adafruit_tsl2591.GAIN_LOW

    def increase_gain(sensor):
        if sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            sensor.gain = adafruit_tsl2591.GAIN_MAX
        elif sensor.gain == adafruit_tsl2591.GAIN_MED:
            sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif sensor.gain == adafruit_tsl2591.GAIN_LOW:
            sensor.gain = adafruit_tsl2591.GAIN_MED

    def read(self):
        # Read and calculate the light level in lux.
        while self.goodRead == 0:
            try:
                # Infrared levels range from 0-65535 (16-bit)
                infrared = self.sensor.infrared
                # Visible-only levels range from 0-2147483647 (32-bit)
                visible = self.sensor.visible
                if infrared < 256 and visible < 256:
                    self.increase_gain(self.sensor)
                else:
                    self.lux = self.sensor.lux
                    self.goodRead = 1
            except RuntimeError as e:
                self.decrease_gain(self.sensor)
            except AttributeError:
                self.lux = None
                self.goodRead = 1

        return self.lux



class Relay:
    """Relay Board CLASS
    :param int address: The address of the sensor
    """

    # Class-level buffer to reduce memory usage and allocations.
    # Note this is NOT thread-safe or re-entrant by design
    _READ_BUF  = bytearray(5)
    _WRITE_BUF = bytearray(5)
    
    def __init__(self, address=_RELAY_ADDR):
        """__init__ Class Initialization

        [extended_summary]

        Parameters
        ----------
        address : `const`, optional
            I2C address of this relay board [Default: _RELAY_ADDR]
        """
        # Initialize the I2C device
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self._device = I2CDevice(self.i2c, address)

        # Make instance variable, and write 0's to relay HAT
        self.relays = [False] * 4
        self.write()


    def read(self):
        """read Read the status of the 4 relays from the board

        [Doesn't really work... not sure why.  Usually just returns
         an array of zeroes.]

        Returns
        -------
        `list` of `byetarray`
            List of the control bit + values from the 4 relays
        """
        # Read the current state of the relays
        self._device.readinto(self._READ_BUF)
        return self._READ_BUF


    def status(self):
        """status Return the current status of the relays

        Method writes the current state to ensure the relays match what
        the internal variables say they should be.  Then this method
        returns the current status.

        Returns
        -------
        `list` of `bool`
            The True/False state of each relay
        """        
        self.write()
        return self.relays


    def write(self):
        """write Write the desired state of thr 4 relays to the board

        [extended_summary]
        """        
        self._WRITE_BUF[0] = _RELAY_COMMAND_BIT
        for i, r in enumerate(self.relays, 1):
            self._WRITE_BUF[i] = 0xff if r else 0x00
        with self._device as i2c:
            i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)
