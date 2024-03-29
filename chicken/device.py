# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: device.py

Control classes for the hardware devices on the Chicken Pi

"""

# Built-In Libraries
from abc import abstractmethod
import datetime
import time

# 3rd Party Libraries

# Hardware Libraries
import adafruit_bus_device.i2c_device  # Adafruit I2C bus device
import adafruit_extended_bus  # Adafruit I2C extended bus
import adafruit_tsl2591  # Outside light sensor
import adafruit_sht31d  # Inside/outside temp/humid sensors (x2)
import adafruit_ahtx0  # Internal (box) temp/humid sensor
import adafruit_motorkit  # Motor HAT
import board  # Adafruit Blinka for direct GPIO control
import digitalio  # Adafruit Blinka for direct GPIO control

# Internal Imports
from chicken import dummy
from chicken import utils

# Module Constants
TEMPHUMID_RESET_HOURS = 24

__all__ = ["set_up_devices"]


def set_up_devices():
    """Set up the sensors and relays

    Initialize each thing inside a try/except, loading in the appropriate
    dummy if the actual sensor cannot be reached.

    Returns
    -------
    sensors: dict
        Dictionary containing the sensor objects
    relays : :class:`Relays`
        The Relays class
    """
    # Inside the Pi box -- AHT10 temp/humid sensor on I2C bus #1
    try:
        box = TempHumid("AHT10", bus=1)
    except ValueError:
        box = dummy.DummyTH()

    # Inside the coop -- SHT30 temp/humid sensor on I2C bus #1
    try:
        inside = TempHumid("SHT30", bus=1)
    except ValueError:
        inside = dummy.DummyTH()

    # Outside the coop -- SHT30 temp/humid sensor on I2C bus #3
    try:
        outside = TempHumid("SHT30", bus=3)
    except ValueError:
        outside = dummy.DummyTH()

    # Outside the coop -- TSL2591 light sensor on I2C bus #3
    try:
        light = TSL2591(bus=3)
    except ValueError:
        light = dummy.DummyLux()

    # Raspberry Pi CPU
    try:
        cpu = RPiCPU()
    except ValueError:
        cpu = dummy.DummyCPU()

    # The relays
    try:
        relays = RelayHAT()  # Use the new KS0212 relay HAT board
    except Exception as err:
        print(f"Relay HAT had error: {err}")
        relays = dummy.Relay()

    # Build the return dictionary + Relays class
    return {
        "box": box,
        "inside": inside,
        "outside": outside,
        "light": light,
        "cpu": cpu,
    }, relays


# ============================================================================#
# Device classes:


# Implementation of the TSL2591 for the chicken-pi
class TSL2591:
    """Chicken-Pi Class for the TSL2591 luminosity sensor

    [extended_summary]
    """

    def __init__(self, bus=3):
        # Initialize the I2C bus.
        self._i2c = adafruit_extended_bus.ExtendedI2C(bus)

        # Initialize the sensor.
        try:
            self._sensor = adafruit_tsl2591.TSL2591(self._i2c)
        except ValueError:
            self._sensor = None

        # Define the attribute here
        self._lux = -999

    # Define functions to increase or decrease the gain
    def decrease_gain(self):
        """Decrease the gain of the TSL2591 sensor

        [extended_summary]
        """
        if self._sensor.gain == adafruit_tsl2591.GAIN_MAX:
            self._sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif self._sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            self._sensor.gain = adafruit_tsl2591.GAIN_MED
        elif self._sensor.gain == adafruit_tsl2591.GAIN_MED:
            self._sensor.gain = adafruit_tsl2591.GAIN_LOW

    def increase_gain(self):
        """Increase the gain of the TSL2591 sensor

        [extended_summary]
        """
        if self._sensor.gain == adafruit_tsl2591.GAIN_HIGH:
            self._sensor.gain = adafruit_tsl2591.GAIN_MAX
        elif self._sensor.gain == adafruit_tsl2591.GAIN_MED:
            self._sensor.gain = adafruit_tsl2591.GAIN_HIGH
        elif self._sensor.gain == adafruit_tsl2591.GAIN_LOW:
            self._sensor.gain = adafruit_tsl2591.GAIN_MED

    def read(self):
        """Read the TSL2591 sensor

        [extended_summary]

        Returns
        -------
        float
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
                    self.increase_gain()
                else:
                    self._lux = self._sensor.lux
                    good_read = True
            except RuntimeError:
                self.decrease_gain()
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
        float
            The calculated light level in LUX
        """
        return self.read()

    @property
    def cache_level(self):
        """Return the cached light level as a class attribute

        [extended_summary]

        Returns
        -------
        float
            The cached light level in LUX
        """
        return self._lux

    @property
    def data_entry(self):
        """Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        float
            Cached sensor values for the database
        """
        return self.cache_level


class TempHumid:
    """Chicken-Pi Class for the various temp/humid sensors

    [extended_summary]

    Parameters
    ----------
    senstyp : str
        The Temp/Humid sensor type to set up
    bus : int, optional
        The I2C bus on which this device is connected (Default: 1)
    """

    def __init__(self, senstyp: str, bus=1):
        self.senstyp = senstyp

        # Load the appropriate I2C Bus
        self._i2c = adafruit_extended_bus.ExtendedI2C(bus)

        # Load the appropriate sensor class
        if senstyp == "SHT30":
            self.sensor = adafruit_sht31d.SHT31D(self._i2c)
        elif senstyp == "AHT10":
            self.sensor = adafruit_ahtx0.AHTx0(self._i2c)
        else:
            raise ValueError("Sensor type must be either SHT30 or AHT10")

        # Internal variables
        self._temp = -99
        self._relh = -99
        self._last_reset = datetime.datetime.now()

    @property
    def temp(self):
        """Returns the sensor temperature as a class attribute

        [extended_summary]

        Returns
        -------
        float
            The requested temperature (ºF)
        """
        # Reset the sensor, if necessary
        self.reset_sensor()

        try:
            self._temp = self.sensor.temperature * 9.0 / 5.0 + 32.0
            return self._temp
        except (RuntimeError, OSError):
            return self.cache_temp

    @property
    def humid(self):
        """Returns the sensor humidity as a class attribute

        [extended_summary]

        Returns
        -------
        float
            The requested humidity (%)
        """
        try:
            self._relh = self.sensor.relative_humidity
            return self._relh
        except (RuntimeError, OSError):
            return self.cache_humid

    @property
    def cache_temp(self):
        """Return the cached temperature as a class attribute

        Returns
        -------
        float
            The cached temperature (ºF)
        """
        return self._temp

    @property
    def cache_humid(self):
        """Return the cached humidity as a class attribute

        Returns
        -------
        float
            The cached humidity (%)
        """
        return self._relh

    @property
    def data_entry(self):
        """Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        tuple of float
            Cached sensor values for the database
        """
        return self.cache_temp, self.cache_humid

    def reset_sensor(self):
        """Reset the sensor if long enough since last reset

        The temperature and humidity sensors sometimes accumulate errors that
        lead to spurious readings.  This method executes a periodic reset of
        the sensors every ``TEMPHUMID_RESET_HOURS``.

        The different sensors have slightly different reset mechanisms, so this
        method queries the ``self.senstyp`` attribute to access the proper
        reset method.

        At present, only running the reset for the AHT10 sensor, as the SHT30
        seems to be stable over long periods.
        """
        # Check sensor type, and elapsed time since last reset
        if self.senstyp != "AHT10" or (
            datetime.datetime.now() - self._last_reset
        ) < datetime.timedelta(hours=TEMPHUMID_RESET_HOURS):
            return

        # Run the reset routine for the AHT10
        self.sensor.reset()
        if not self.sensor.calibrate():
            raise RuntimeError("Could not calibrate AHT10 Sensor")
        # Record the time of the reset
        self._last_reset = datetime.datetime.now()


class ChickenDoor:
    """Chicken-Pi Class for the yet-to-be-built chicken door

    [extended_summary]
    """

    def __init__(self):
        self.kit = adafruit_motorkit.MotorKit()

    def test_motor(self):
        """Test the Motor!

        [extended_summary]
        """
        self.kit.motor1.throttle = 1.0
        time.sleep(0.5)
        self.kit.motor1.throttle = 0.0

    def open_door(self):
        """Open the door!

        _extended_summary_
        """


class RPiCPU:
    """RPiCPU [summary]

    [extended_summary]
    """

    def __init__(self):
        pass

    @property
    def temp(self):
        """Return the CPU temperature as a class attribute

        [extended_summary]

        Returns
        -------
        float
            The CPU temperature in ºF, as reported by the system
        """
        return self.get_cpu_temp()

    @property
    def data_entry(self):
        """Return the DATA_ENTRY object needed for the database

        [extended_summary]

        Returns
        -------
        float
            The CPU temperature (ºF)
        """
        return self.temp

    @staticmethod
    def get_cpu_temp():
        """Read the CPU temperature from system file

        [extended_summary]

        Returns
        -------
        float
            CPU temperature in ºF
        """
        # Check Pi CPU Temp:
        if utils.get_system_type() == "Linux":
            cputemp_fn = "/sys/class/thermal/thermal_zone0/temp"
            with open(cputemp_fn, "r", encoding="utf-8") as sys_file:
                return (float(sys_file.read()) / 1000.0) * 9.0 / 5.0 + 32.0
        return None


# Relay Classes ====================================================#
class RelayBase:
    """Base Relay Class

    This base class cane be used with any implementation of relay control
    used with the chicken-pi.
    """

    def __init__(self):
        # Make instance variable, and write 0's to relays
        self.good_write = None
        self.state = [False] * 4

    def status(self):
        """Return the current status of the relays

        Method writes the current state to ensure the relays match what
        the internal variables say they should be.  Then this method
        returns the current status.

        Returns
        -------
        list of bool
            The True/False state of each relay
        """
        self.write()
        return self.state

    @abstractmethod
    def read(self):
        """Read the current state of the relays

        This method must be implemented by hardware-specific code
        """

    @abstractmethod
    def write(self):
        """Write the current demand to the relays

        This method must be implemented by hardware-specific code
        """


class Old3ARelay(RelayBase):
    """Chicken-Pi Class for the _____ Relay Board

    This is the class for the original 3A Relay DDL board

    These were removed in Jan 2023 in favor of a 10A relay board
    """

    # Class-level buffer to reduce memory usage and allocations.
    # Note this is NOT thread-safe or re-entrant by design
    _READ_BUF = bytearray(5)
    _WRITE_BUF = bytearray(5)

    # Internal constants:
    _RELAY_ADDR = 0x10
    _RELAY_COMMAND_BIT = 0x01

    def __init__(self, address=_RELAY_ADDR):
        """__init__ Class Initialization

        [extended_summary]

        Parameters
        ----------
        address : `const`, optional
            I2C address of this relay board [Default: _RELAY_ADDR]
        """
        super().__init__()

        # Initialize the I2C device
        self._i2c = adafruit_extended_bus.ExtendedI2C(1)
        self._device = adafruit_bus_device.i2c_device.I2CDevice(self._i2c, address)

        self.write()

    def read(self):
        """Read the current state of the relays

        [Doesn't really work... not sure why.  Usually just returns
         an array of zeroes.]

        Returns
        -------
        list of byetarray
            List of the control bit + values from the 4 relays
        """
        # Read the current state of the relays
        self._device.readinto(self._READ_BUF)
        return self._READ_BUF

    def write(self):
        """Write the current demand to the relays

        [extended_summary]
        """
        try:
            self._WRITE_BUF[0] = self._RELAY_COMMAND_BIT
            for i, relay in enumerate(self.state, 1):
                self._WRITE_BUF[i] = 0xFF if relay else 0x00
            with self._device as i2c:
                i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)
            self.good_write = True
        except OSError as error:
            print(f"i2c threw exception: {error}")
            self.good_write = False


class RelayHAT(RelayBase):
    """Relay HAT Control Class

    This is the control class for the KS0212 relay HAT board installed in the
    chicken-pi in January 2023.

    Unlike the 3A Relay DDL board that was installed in the chicken-pi's prior
    to January 2023, these relay boards are directly controlled by toggling
    GPIO pins.  The previous boards were controlled by I2C
    If you test with other code like Python code, you should use BCM port and
    set the corresponding port 4 22 6 26.
    """

    def __init__(self):
        super().__init__()

        # Initialize the GPIO pins needed
        self.pins = [
            digitalio.DigitalInOut(board.D4),
            digitalio.DigitalInOut(board.D22),
            digitalio.DigitalInOut(board.D6),
            digitalio.DigitalInOut(board.D26),
        ]
        # Set pin direction
        for pin in self.pins:
            pin.direction = digitalio.Direction.OUTPUT

        self.write()

    def read(self):
        """Read the current state of the relays"""

        return [pin.value for pin in self.pins]

    def write(self):
        """Write the current demand to the relays

        [extended_summary]
        """

        try:
            for pin, demand in zip(self.pins, self.state):
                pin.value = demand
            self.good_write = True

        except Exception as err:
            print(f"We had a problem with writing to the RelayHAT: {err}")
            self.good_write = False
