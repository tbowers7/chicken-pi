#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: display_coop_values.py

Displays the values from chicken-pi sensors to the screen for visual inspection.

"""

# Futures
# […]

# Built-in/Generic Imports
from tkinter import *      # Tk for display window
import time                # for the sleep() function
import datetime            # date & time
import os,sys              # Search for file on disk
import csv                 # For CSV output
import atexit              # Register cleanup functions
import numpy as np         # Numpy!
# […]

# Libs
import board               # Access to Raspberry Pi's GPIO pins
import adafruit_dht        # DHT library
# […]

# Own modules
#from {path} import {class}
import chicken_tsl2591 as tsl


## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 1 - Planning'


"""
  Layout of this file:
  1.  Define the DISPLAY STRING & open file for write
  2.  Method for updating DISPLAY STRING
  3.  Call the loop for Tk to DISPLAY STRING
"""

### Display Strings
DHT1Str = "Outside"
DHT3Str = "Roosts "
DHT2Str = "NestBox"



# (1) Define the DISPLAY STRING & open file for write
root = Tk()
val1 = ''
lineswrote=0
disp = Label(root, font=('courier', 18, 'bold'), bg='black', fg='yellow')
disp.pack(fill=BOTH, expand=1)

# Check to see if CSV file exists in the script directory, if no,
# write header.  Set up CSV file for writing, including close @ exit
abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
fn = abspath+'/temp_values.csv'
if not os.path.isfile(fn):
    csvfile = open(fn, 'w', newline='')
    csvfile.write("date,time,t1,h1,t2,h2,t3,h3,cpu,lux\n")
else:
    csvfile = open(fn, 'a', newline='')
atexit.register(csvfile.close)
datawriter = csv.writer(csvfile, delimiter=',',quotechar=' ',
                        quoting=csv.QUOTE_MINIMAL)


# (2) Method for updating DISPLAY STRING
def update():
    global val1         # Make available globally
    global lineswrote   # Make available globally
    
    # Start up the DHT sensors
    dht1 = adafruit_dht.DHT22(board.D19)
    dht2 = adafruit_dht.DHT22(board.D20)
    dht3 = adafruit_dht.DHT22(board.D21)
    
    # Create list and arrays for reading loop
    dhts     = [dht1, dht2, dht3]
    tc       = np.empty(3)
    hm       = np.empty(3)
    dhtnames = [DHT1Str, DHT2Str, DHT3Str]
    
    ### Read from the DHT sensors
    for sens, i in zip(dhts, [0,1,2]):

        goodRead = False
        readTries = 0
        while goodRead == False:
            if readTries > 100: # Don't wait too long... if no goodRead, move on
                tc[i] = 0
                hm[i] = 0
                break
            try:
                tc[i] = sens.temperature
                hm[i] = sens.humidity
                if hm[i] < 100 and tc[i] < 100:         # Quality control
                    goodRead = True
                else:
                    time.sleep(0.1)    # Wait a moment, and try again
                    readTries += 1
            except:
                time.sleep(0.1)  # If error, wait a moment, and try again
                readTries += 1
    
    ### Once we have good readings from all three sensors, do the C -> F
    ### conversion and then create the output string (numpy is our friend)
    tf = tc * (9. / 5.) + 32.
    
    ### Shut down the DHT pulseio's to minimize CPU heating from having
    ### the libgpio_pulsed processes running constantly
    for sens in dhts:
        sens.pulse_in.deinit()
    
    ### Also read from the on-board temperature sensors on the Pi
    cputemp_fn = "/sys/class/thermal/thermal_zone0/temp"
    f = open(cputemp_fn,"r")
    if f.mode == 'r':
        cpuTemp = float(f.read())/1000.
    f.close()
    
    ### Now, read from the TSL2591 light sensor on I2C
    light = tsl.Read()
    lux = light.read()
    # Make LUX string, depending on value of lux
    if lux < 10:
        luxstr = '{:0.2f}'.format(lux)
    elif lux < 100:
        luxstr = '{:0.1f}'.format(lux)
    else:
        luxstr = '{:0.0f}'.format(lux)
        
    # String includes:
    #   DATE
    #   DHT1: Temp, Humidity
    #   DHT2: Temp, Humidity
    #   DHT3: Temp, Humidity
    #   Light: Lux
    #   CPU: CPU_Temp
    
    now = datetime.datetime.now()

    # Create the output DHT strings for display, with case for "NO DATA"
    dhtstrs = []
    for i in [0,1,2]:
        if tc[i] == 0 and hm[i] == 0:
            dhtstrs.append("{:s}:    NO DATA   ".format(dhtnames[i]))
        else:
            dhtstrs.append("{:s}: {:0.1f}\xb0F, {:0.1f}%".format(dhtnames[i],
                                                                 tf[i], hm[i]))
    
    val2 = "{:s}\n\n {:s} \n {:s} \n {:s} \n Light: {:s} lux \n CPU: {:0.1f}\xb0C [< 85\xb0C] ".format(
        now.strftime("%d-%b-%y %H:%M:%S"),dhtstrs[0],dhtstrs[1],dhtstrs[2],
        luxstr, cpuTemp)
    
    # Update the DISPLAY STRING
    if val2 != val1:
        val1 = val2
        disp.config(text=val2)
    
    # Write a line to the CSV file
    datawriter.writerow([now.strftime("%Y-%m-%d"),now.strftime("%H:%M:%S"),
                         "{:0.2f},{:0.1f},{:0.2f},{:0.1f},{:0.2f},{:0.1f},{:0.1f},{:s}".format(tf[0], hm[0], tf[1], hm[1], tf[2], hm[2], cpuTemp, luxstr)])
    lineswrote += 1
    
    if lineswrote >= 20:     # Write data to file every 20 lines
        csvfile.flush()      #  (Rougly every 2 minutes at a 5 second refresh)
        os.fsync(csvfile.fileno())
        lineswrote = 0
    
    
    # This Method calls itself every 5s to update the display
    disp.after(5000, update)
        


# (3) Call the loop for Tk to DISPLAY STRING
update()
root.winfo_toplevel().title("Chicken Coop Sensor Values")
root.geometry("+600+0")
root.mainloop()
