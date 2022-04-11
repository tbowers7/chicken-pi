# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.#
#
#  Created on 10-Apr-2022
#
#  @author: tbowers

"""
    MODULE: monitor_pi
    FILE: device.py

Control classes for the hardware devices on the Chicken Pi

"""

# Built-In Libraries
import os
import time

# 3rd Party Libraries

# Hardware Libraries

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_extended_bus import ExtendedI2C as EI2C
import adafruit_tsl2591  # Outside light sensor
import adafruit_sht31d  # Inside/outside temp/humid sensors (x2)
import adafruit_ahtx0  # Internal (box) temp/humid sensor
from adafruit_motorkit import MotorKit  # Motor HAT

# Internal Imports

# Enable testing on both Raspberry Pi and Mac
if os.path.exists("/usr/bin/uname"):
    _UNAME = "/usr/bin/uname"
elif os.path.exists("/bin/uname"):
    _UNAME = "/bin/uname"
else:
    _UNAME = ""
SYSTYPE = (os.popen(f"{_UNAME} -a").read()).split()[0]


def set_up_sensors():
    """set_up_sensors Set up the sensors

    [extended_summary]

    Returns
    -------
    `dict`
        Dictionary containing the sensor objects
    """
    # Use a dictionary for holding the sensor instances
    sensors = {}

    # Inside the Pi box -- AHT10 temp/humid sensor to monitor conditions
    sensors["box"] = TempHumid("AHT10")

    # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
    sensors["inside"] = TempHumid("SHT30", bus=1)

    # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
    sensors["outside"] = TempHumid("SHT30", bus=3)

    # Outside the coop -- TSL2591 light sensor
    sensors["light"] = TSL2591()

    # Raspberry Pi CPU
    sensors["cpu"] = RPiCPU()

    return sensors


# =============================================================================#

# Device classes:

# Implementation of the TSL2591 for the chicken-pi
class TSL2591:
    """ Chicken-Pi Class for the TSL2591 luminosity sensor

    [extended_summary]
    """

    def __init__(self, bus=3):
        # Initialize the I2C bus.
        self._i2c = EI2C(bus)

        # Initialize the sensor.
        try:
            self._sensor = adafruit_tsl2591.TSL2591(self._i2c)
        except ValueError:
            self._sensor = None

        # Define the attribute here
        self._lux = -999

    # Define functions to increase or decrease the gain
    def decrease_gain(self, sensor):
        """decrease_gain Decrease the gain of the TSL2591 sensor

        [extended_summary]

        Parameters
        ----------
        sensor : `adafruit_tsl2591.TSL2591`
            The sensor instance
        """
        if sensor.gain == adafruit_tsl2591.GAIN_MAX:
            sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            sensor.gain = adafruit_tsl2591.GAIN_MED
        elif sensor.gain == adafruit_tsl2591.GAIN_MED:
            sensor.gain = adafruit_tsl2591.GAIN_LOW

    def increase_gain(self, sensor):
        """increase_gain Increase the gain of the TSL2591 sensor

        [extended_summary]

        Parameters
        ----------
        sensor : `adafruit_tsl2591.TSL2591`
            The sensor instance
        """
        if sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            sensor.gain = adafruit_tsl2591.GAIN_MAX
        elif sensor.gain == adafruit_tsl2591.GAIN_MED:
            sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif sensor.gain == adafruit_tsl2591.GAIN_LOW:
            sensor.gain = adafruit_tsl2591.GAIN_MED

    def read(self):
        """read Read the TSL2591 sensor

        [extended_summary]

        Returns
        -------
        `float`
            The calculated light level in LUX
        """
        good_read = False

        # Read and calculate the light level in lux.
        while not good_read:
            try:
                # Infrared levels range from 0-65535 (16-bit)
                infrared = self._sensor.infrared
                # Visible-only levels range from 0-2147483647 (32-bit)
                visible = self._sensor.visible
                if infrared < 256 and visible < 256:
                    self.increase_gain(self._sensor)
                else:
                    self._lux = self._sensor.lux
                    good_read = True
            except RuntimeError:
                self.decrease_gain(self._sensor)
            except AttributeError:
                self._lux = None
                good_read = True

        return self._lux

    @property
    def level(self):
        """level Return the light level as a class attribute

        [extended_summary]

        Returns
        -------
        `float`
            The calculated light level in LUX
        """
        return self.read()

    @property
    def cache_level(self):
        """cache_level Return the cached light level as a class attribute

        [extended_summary]

        Returns
        -------
        `float`
            The cached light level in LUX
        """
        return self._lux

    @property
    def data_entry(self):
        """data_entry Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        `float`
            Cached sensor values for the database
        """
        return self.cache_level


class Relay:
    """ Chicken-Pi Class for the _____ Relay Board

    [extended_summary]
    """

    # Internal constants:
    _RELAY_ADDR = 0x10
    _RELAY_COMMAND_BIT = 0x01

    # Class-level buffer to reduce memory usage and allocations.
    # Note this is NOT thread-safe or re-entrant by design
    _READ_BUF = bytearray(5)
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
        self.good_write = None
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
        try:
            self._WRITE_BUF[0] = self._RELAY_COMMAND_BIT
            for i, relay in enumerate(self.state, 1):
                self._WRITE_BUF[i] = 0xFF if relay else 0x00
            with self._device as i2c:
                i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)
            self.good_write = True
        except OSError as e:
            print(f"i2c threw exception: {e}")
            self.good_write = False


class TempHumid:
    """ Chicken-Pi Class for the TSL2591 luminosity sensor

    [extended_summary]
    """

    def __init__(self, senstyp, bus=1):

        # Load the appropriate I2C Bus
        self._i2c = EI2C(bus)

        # Load the appropriate sensor class
        if senstyp == "SHT30":
            self.sensor = adafruit_sht31d.SHT31D(self._i2c)
        elif senstyp == "AHT10":
            # TODO: AHT10 seems to accumulate weirdly -- see about resetting before each read
            self.sensor = adafruit_ahtx0.AHTx0(self._i2c)
        else:
            raise ValueError("Sensor type must be either SHT30 or AHT10")

        # Internal variables
        self._temp = -99
        self._relh = -99

    @property
    def temp(self):
        """temp Returns the sensor temperature as a class attribute

        [extended_summary]

        Returns
        -------
        `float`
            The requested temperature (ºF)
        """
        try:
            self._temp = self.sensor.temperature * 9.0 / 5.0 + 32.0
            return self._temp
        except (RuntimeError, OSError):
            return self.cache_temp

    @property
    def humid(self):
        """humid Returns the sensor humidity as a class attribute

        [extended_summary]

        Returns
        -------
        `float`
            The requested humidity (%)
        """
        try:
            self._relh = self.sensor.relative_humidity
            return self._relh
        except (RuntimeError, OSError):
            return self.cache_humid

    @property
    def cache_temp(self):
        """cache_temp Return the cached temperature as a class attribute

        Returns
        -------
        `float`
            The cached temperature (ºF)
        """
        return self._temp

    @property
    def cache_humid(self):
        """cache_humid Return the cached humidity as a class attribute

        Returns
        -------
        `float`
            The cached humidity (%)
        """
        return self._relh

    @property
    def data_entry(self):
        """data_entry Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        `float`, `float`
            Cached sensor values for the database
        """
        return self.cache_temp, self.cache_humid


class ChickenDoor:
    """ Chicken-Pi Class for the yet-to-be-built chicken door

    [extended_summary]
    """

    def __init__(self):
        self.kit = MotorKit()

    def test_motor(self):
        """test_motor Test the Motor!

        [extended_summary]
        """
        self.kit.motor1.throttle = 1.0
        time.sleep(0.5)
        self.kit.motor1.throttle = 0.0


class RPiCPU:
    """RPiCPU [summary]

    [extended_summary]
    """

    def __init__(self):
        pass

    @property
    def temp(self):
        """temp Return the CPU temperature as a class attribute

        [extended_summary]

        Returns
        -------
        `float`
            The CPU temperature in ºF, as reported by the system
        """
        return get_cpu_temp()

    @property
    def data_entry(self):
        """data_entry Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        `float`
            The CPU temperature (ºF)
        """
        return self.temp


def get_cpu_temp():
    """get_cpu_temp Read the CPU temperature from system file

    [extended_summary]

    Returns
    -------
    `float`
        CPU temperature in ºF
    """
    # Check Pi CPU Temp:
    if SYSTYPE == "Linux":
        cputemp_fn = "/sys/class/thermal/thermal_zone0/temp"
        with open(cputemp_fn, "r") as sys_file:
            return (float(sys_file.read()) / 1000.0) * 9.0 / 5.0 + 32.0
    return None
