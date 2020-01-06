# implementation of the TSL2591 for the chicken-pi

import time
import board
import busio
import adafruit_tsl2591

# Initialize the I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the sensor.
sensor = adafruit_tsl2591.TSL2591(i2c)

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

class Read:
    def __init__(self):
        self.goodRead = 0

    def read(self):
        # Read and calculate the light level in lux.
        while self.goodRead == 0:
            try:
                # Infrared levels range from 0-65535 (16-bit)
                infrared = sensor.infrared
                # Visible-only levels range from 0-2147483647 (32-bit)
                visible = sensor.visible
                if infrared < 60 and visible < 60:
                    increase_gain(sensor)
                else:
                    self.lux = sensor.lux
                    self.goodRead = 1
            except RuntimeError as e:
                decrease_gain(sensor)
                
        return self.lux
