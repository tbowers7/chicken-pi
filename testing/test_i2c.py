# I2C Scan -- CircuitPython
import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice

from micropython import const

_ADDR        = const(0x10)  # Address of the relay board
_COMMAND_BIT = const(0x01)  # Apparent command bit of relay board



with busio.I2C(board.SCL, board.SDA) as i2c:
    device = I2CDevice(i2c, _ADDR, probe=True)
    bytes_read = bytearray(5)
    bytes_read2 = bytearray(5)
    bytes_write = bytearray(5)
    with device as i2c:
        bytes_read[0] = const(0x00)
        i2c.readinto(bytes_read)
        print(f"I read this: {bytes_read}")
        for i in range(1,5):
            print(f"Position {i} is {bytes_read[i] != 0x00}")

            
    # Add command bit
    bytes_write[0] = _COMMAND_BIT
    for jj in range(0,16):
        print(f"\nDecimal value to write: {jj}, Binary bits to write: {jj&1}, {jj&2}, {jj&4}, {jj&8}")
        for kk in range(4):
            bytes_write[kk+1] = jj & int(2**kk)
        print(f"I will write this: {bytes_write}")
        for i in range(1,5):
            print(f"Writing position {i} as {bytes_write[i] != 0x00}")

        with device as i2c:
            # Write this back to the I2C device
            bytes_read[0] = const(0x00)
            i2c.readinto(bytes_read)
            print(f"Before writing, I read this: {bytes_read}")

        with device as i2c:
            print(f"Here's what will be sent to the relay: {bytes_write}")
            i2c.write_then_readinto(bytes_write, bytes_read2)
            print(f"This is what the relay says was written: {bytes_read2}")
            print(f"This is the device address: {hex(device.device_address)}")   
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
