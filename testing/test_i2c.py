# I2C Scan -- CircuitPython
import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice

from micropython import const

_ADDR        = const(0x10)  # Address of the relay board
_COMMAND_BIT = const(0xA0)  # Command bit of TSL2591



with busio.I2C(board.SCL, board.SDA) as i2c:
    device = I2CDevice(i2c, _ADDR)
    bytes_read = bytearray(5)
    bytes_read2 = bytearray(5)
    bytes_write = bytearray(5)
    with device:
        device.readinto(bytes_read)
        print(bytes_read)
        for i in range(1,5):
            print(bytes_read[i] != 0x00)

            
        # Add command bit
        bytes_write[0] = 0x01 # Apparent command byte needed for relay board
        for jj in range(0,16):
            print(jj, jj&1, jj&2, jj&4, jj&8)
            bytes_write[1] = jj & 1
            bytes_write[2] = jj & 2
            bytes_write[3] = jj & 4
            bytes_write[4] = jj & 8
            print(bytes_write)
            for i in range(1,5):
                print(bytes_write[i] != 0x00)

            # Write this back to the I2C device
            print(bytes_write)
            device.write_then_readinto(bytes_write, bytes_read2)
            print(bytes_read2)
            time.sleep(1)
    

#while not i2c.try_lock():
 #    pass 
#
#print("I2C addresses found:", [hex(device_address)
#                               for device_address in i2c.scan()])
#time.sleep(2)

# Find a way to read from the i2c simply.
#i2c.unlock()

##_BUFFER = bytearray()

#i2c.readfrom_into(_ADDR, _BUFFER)

#print(hex(_ADDR),_BUFFER)
