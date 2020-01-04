#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
  FILE: display_coop_values.py

Displays the values from chicken-pi sensors to the screen for visual inspection.

"""

# Futures
# […]

# Built-in/Generic Imports
# […]

# Libs
from tkinter import *
import time
import datetime
import adafruit_dht
import board
import numpy as np
# […]

# Own modules
#from {path} import {class}
# […]


## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi@gmail.com'
__status__ = 'Development Status :: 1 - Planning'


"""
  Layout of this file:
  1.  Define the DISPLAY STRING
  2.  Method for updating DISPLAY STRING
  3.  Call the loop for Tk to DISPLAY STRING
"""
# (1) Define the DISPLAY STRING
root = Tk()
val1 = ''
disp = Label(root, font=('courier', 25, 'bold'), bg='black', fg='yellow')
disp.pack(fill=BOTH, expand=1)

dht1 = adafruit_dht.DHT22(board.D19)
dht2 = adafruit_dht.DHT22(board.D20)
dht3 = adafruit_dht.DHT22(board.D21)




# (2) Method for updating DISPLAY STRING
def update():
    global val1   # Make val1 available globally

    # Create list and arrays for reading loop
    dhts = [dht1, dht2, dht3]
    tc = np.empty(3)
    hm = np.empty(3)
    
    ### Read from the DHT sensors
    for sens, i in zip(dhts, [0,1,2]):
        
        goodRead = False
        while goodRead == False:
            try:
                tc[i] = sens.temperature
                hm[i] = sens.humidity
                if hm[i] < 100 and tc[i] < 100:         # Quality control
                    goodRead = True
                else:
                    time.sleep(0.1)    # Wait a moment, and try again
            except:
                time.sleep(0.1)  # If error, wait a moment, and try again


    ### Once we have good readings from all three sensors, do the C -> F
    ### conversion and then create the output string (numpy is our friend)
    tf = tc * (9. / 5.) + 32.

    # String includes:
    #   DATE
    #   DHT1: Temp, Humidity
    #   DHT2: Temp, Humidity
    #   DHT3: Temp, Humidity
    
    now = datetime.datetime.now()
    val2 = "{0:s}\n\n DHT #1: {1:0.1f}\xb0F, {2:0.1f}% \n DHT #2: {3:0.1f}\xb0F, {4:0.1f}% \n DHT #3: {5:0.1f}\xb0F, {6:0.1f}% ".format(
        now.strftime("%d-%b-%y %H:%M:%S"),
        tf[0], hm[0], tf[1], hm[1], tf[2], hm[2])

    # Update the DISPLAY STRING
    if val2 != val1:
        val1 = val2
        disp.config(text=val2)

    # This Method calls itself every 5s to update the display
    disp.after(5000, update)
        


# (3) Call the loop for Tk to DISPLAY STRING
update()
root.winfo_toplevel().title("Chicken Coop Sensor Values")
root.mainloop()
