
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
            #print("In Realy.read()...")
            #print(self._READ_BUF)
            #for i in range(1,5):
            #    print(self._READ_BUF[i] != 0x00)
            return self._READ_BUF





def read_relay():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = Relay(i2c)
    return sensor.read()
