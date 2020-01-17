
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

# Internal constants:
_RELAY_ADDR        = const(0x10)
_RELAY_COMMAND_BIT = const(0x01)

class Relay:
    """Relay Board
    :param busio.I2C i2c: The I2C bus connected to the sensor
    :param int address: The address of the sensor
    """

    # Class-level buffer to reduce memory usage and allocations.
    # Note this is NOT thread-safe or re-entrant by design
    _READ_BUF  = bytearray(5)
    _WRITE_BUF = bytearray(5)
    
    def __init__(self, i2c, address=_RELAY_ADDR):
        self._device = I2CDevice(i2c, address)
        

    def read(self):
        # Read the current state of the relays
        with self._device as i2c:
            i2c.readinto(self._READ_BUF)
            return self._READ_BUF

    def write(self, r1, r2, r3, r4):
        self._WRITE_BUF[0] = _RELAY_COMMAND_BIT
        self._WRITE_BUF[1] = 0xff if r1 else 0x00
        self._WRITE_BUF[2] = 0xff if r2 else 0x00
        self._WRITE_BUF[3] = 0xff if r3 else 0x00
        self._WRITE_BUF[4] = 0xff if r4 else 0x00
        with self._device as i2c:
            i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)


### User-facing functions

def read_relay():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = Relay(i2c)
    return sensor.read()

def write_relay(r1, r2, r3, r4):      ### r1 - r4 are type BOOL
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = Relay(i2c)
    sensor.write(r1, r2, r3, r4)
