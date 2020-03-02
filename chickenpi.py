#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: chickenpi.py

Main driver routine for the integrated Chicken-Pi setup.

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
#import board               # Access to Raspberry Pi's GPIO pins
#import adafruit_dht        # DHT library
# […]

# Own modules
#from {path} import {class}
#import chicken_tsl2591 as tsl
from chicken_status import *
from chicken_graphs import *

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.2.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 2 - Pre-Alpha'

PI_TOOLBAR = 36
TK_HEADER  = 25


class Control_Window:
    """
    Control_Window class
    Creates the main control window and also spawns the secondary display
    windows.
    """
    def __init__(self, master):
        """
        __init__: initializes the class, including geometry and spawning
        display windows
        """
        self.master = master
        self.master.geometry("600x400+0+{:d}".format(PI_TOOLBAR))
        self.master.title("Control Window")
        self.frame  = Frame(self.master)
        self.label = Label(self.frame, text="This is the control window")
        self.label.pack()
        self.frame.pack()
        self.newStatus = Toplevel(self.master)
        self.win1 = Status_Window(self.newStatus)
        self.newGraphs = Toplevel(self.master)
        self.win2 = Graphs_Window(self.newGraphs)
        
    def update(self):
        """
        update: method for updating the display windows
        """
        self.win1.update()
        self.frame.after(5000, self.update)
        


### Main Routine ###
root = Tk()
app = Control_Window(root)
try:
    app.update()
    root.mainloop()
finally:
    print("Ending...")
