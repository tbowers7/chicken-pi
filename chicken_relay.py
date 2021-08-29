
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

# Internal constants:
_RELAY_ADDR        = const(0x10)
_RELAY_COMMAND_BIT = const(0x01)

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
        i2c = busio.I2C(board.SCL, board.SDA)
        self._device = I2CDevice(i2c, address)
        

    def read(self):
        """read Read the status of the 4 relays from the board

        [extended_summary]

        Returns
        -------
        `list` of `byetarray`
            List of the values from the 4 relays
        """
        # Read the current state of the relays
        with self._device as i2c:
            i2c.readinto(self._READ_BUF)
            return self._READ_BUF


    def write(self, rel):
        """write Write the desired state of thr 4 relays to the board

        [extended_summary]

        Parameters
        ----------
        r : `list` of `bool`
            List of the 4 T/F values to set on the relay board
        """
        self._WRITE_BUF[0] = _RELAY_COMMAND_BIT
        for i, r in enumerate(rel, 1):
            self._WRITE_BUF[i] = 0xff if r else 0x00
        with self._device as i2c:
            i2c.write_then_readinto(self._WRITE_BUF, self._READ_BUF)
