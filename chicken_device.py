# -*- coding: utf-8 -*-

"""
  FILE: chicken_devices.py

Control classes for the hardware devices on the Chicken Pi

"""

# Built-in/Generic Imports
import time
# […]

# Libs
import numpy as np         # Numpy!

# Hardware Libs
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_extended_bus import ExtendedI2C as EI2C
import adafruit_tsl2591                 # Outside light sensor
import adafruit_sht31d                  # Inside/outside temp/humid sensors (x2)
import adafruit_ahtx0                   # Internal (box) temp/humid sensor
from adafruit_motorkit import MotorKit  # Motor HAT

# Own modules
#from {path} import {class}


def set_up_sensors():

    # Use a dictionary for holding the sensor instances
    sensors = {}

    # Inside the Pi box -- AHT10 temp/humid sensor to monitor conditions
    sensors['box'] = TempHumid('AHT10')

    # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
    sensors['inside'] = TempHumid('SHT30', bus=1)

    # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
    sensors['outside'] = TempHumid('SHT30', bus=3)

    # Outside the coop -- TSL2591 light sensor
    sensors['light'] = TSL2591()

    return sensors


#=============================================================================#

# Device classes:

# Implementation of the TSL2591 for the chicken-pi
class TSL2591:

    def __init__(self, bus=3):
        # Initialize the I2C bus.
        self._i2c = EI2C(bus)

        # Initialize the sensor.
        try:
            self._sensor = adafruit_tsl2591.TSL2591(self._i2c)
        except ValueError:
            self._sensor = None
        
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
                infrared = self._sensor.infrared
                # Visible-only levels range from 0-2147483647 (32-bit)
                visible = self._sensor.visible
                if infrared < 256 and visible < 256:
                    self.increase_gain(self._sensor)
                else:
                    self.lux = self._sensor.lux
                    self.goodRead = 1
            except RuntimeError as e:
                # print(f"Error kicked: {e}")
                self.decrease_gain(self._sensor)
            except AttributeError:
                self.lux = None
                self.goodRead = 1

        return self.lux



class Relay:
    """Relay Board CLASS
    :param int address: The address of the sensor
    """

    # Internal constants:
    _RELAY_ADDR        = 0x10
    _RELAY_COMMAND_BIT = 0x01

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
        self._i2c = EI2C(1)
        self._device = I2CDevice(self._i2c, address)

        # Make instance variable, and write 0's to relay HAT
        self.state = [False] * 4
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
        return self.state


    def write(self):
        """write Write the desired state of thr 4 relays to the board

        [extended_summary]
        """        
        self._WRITE_BUF[0] = self._RELAY_COMMAND_BIT
        for i, r in enumerate(self.state, 1):
            self._WRITE_BUF[i] = 0xff if r else 0x00
        with self._device as i2c:
            i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)


class TempHumid:

    def __init__(self, senstyp, bus=1):

        # Load the appropriate I2C Bus
        self._i2c = EI2C(bus)

        # Load the appropriate sensor class
        if senstyp == 'SHT30':
            self.sensor = adafruit_sht31d.SHT31D(self._i2c)
        elif senstyp == 'AHT10':
            self.sensor = adafruit_ahtx0.AHTx0(self._i2c)
        else:
            raise ValueError('Sensor type must be either SHT30 or AHT10')

        # Internal variables
        self._temp = -99
        self._relh = -99

    @property
    def temp(self):
        try:
            self._temp = self.sensor.temperature * 9./5. + 32.
            return self._temp
        except:
            return self.cache_temp

    @property
    def humid(self):
        try:
            self._relh = self.sensor.relative_humidity
            return self._relh
        except:
            return self.cache_humid

    @property
    def cache_temp(self):
        return self._temp

    @property
    def cache_humid(self):
        return self._relh


class ChickenDoor:

    def __init__(self):
        self.kit = MotorKit()

    def test_motor(self):
        self.kit.motor1.throttle = 1.0
        time.sleep(0.5)
        self.kit.motor1.throttle = 0.0
