
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
