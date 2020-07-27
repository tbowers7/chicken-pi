# -*- coding: utf-8 -*-

"""
  FILE: chicken_status.py

Status display window, updates frequently with current values

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
# […]

# Own modules
#from {path} import {class}


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

### Constants
WIDGET_WIDE  = 600           # Width of the "Status Window"
WIDGET_HIGH  = 200           # Height of the "Status Window"
STATBG     = 'black'


class StatusWindow():
    """
    StatusWindow class
    Creates the status window and (supposedly) updates it from time to time.
    """
    def __init__(self, master, CONTROL_WIDTH):
        """
        __init__ method: initializes the Status Window
        """
        ## Define the MASTER for the window
        self.master = master
        
        ## Define the geometry and title for the status window
        self.master.geometry("{:d}x{:d}+{:d}+{:d}".format(
            WIDGET_WIDE,WIDGET_HIGH,CONTROL_WIDTH+10,PI_TOOLBAR))
        self.master.title("Status Window")
        self.master.configure(bg=STATBG)
        
        ## A "frame" holds the various window contents
        self.frame = Frame(self.master, bg=STATBG)
        self.frame.pack(expand=0)
        
        ## Time at the top
        self.disptime = Label(self.frame, font=('courier', 12, 'bold'),
                              bg=STATBG, fg='lightblue')
        self.disptime.grid(row=0, columnspan=4)
        
        ## Next, label for environmental statuses
        Label(self.frame, font=('times', 12, 'bold'), fg='yellow',
              bg=STATBG,text='Environmental Status').grid(row=1, columnspan=4)

        ## And now, the actual statuses:
        stattext1 = 'Outside:\nNests:\nRoosts:'
        stattext2 = 'Light:\nCPU:'
        Label(self.frame, font=('courier', 12, 'bold'), fg='lightgreen',
              bg=STATBG, text=stattext1).grid(row=2, column=0)
        Label(self.frame, font=('courier', 12, 'bold'), fg='lightgreen',
              bg=STATBG, text=stattext2).grid(row=2, column=2)
        self.envstat1 = Label(self.frame, font=('courier', 12, 'bold'),
                             bg=STATBG, fg='green')
        self.envstat1.grid(row=2, column=1)
        self.envstat2 = Label(self.frame, font=('courier', 12, 'bold'),
                             bg=STATBG, fg='green')
        self.envstat2.grid(row=2, column=3)
        self.count = 0
        
        
    def close_window(self):
        self.master.destroy()
        
        
    def update(self):
        now = datetime.datetime.now()
        self.disptime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))
        #self.frame.after(5000, self.update)
        self.count += 1
        self.envstat1.config(text='{:d}\n{:d}\n{:d}'.format(
            self.count,self.count+1,self.count+2))
        self.envstat2.config(text='{:d}\n{:d}'.format(
            self.count+3,self.count+4))
