# -*- coding: utf-8 -*-

"""
  FILE: chicken_control.py

Control window, with all the shiny knobs and buttons

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

### Constants
OUT1STR      = "Roost Lamp"  # Name of what is plugged into outlet #1
OUT2STR      = "Red Light "  # Name of what is plugged into outlet #2
OUT3STR      = "Nest Lamp "  # Name of what is plugged into outlet #3
OUT4STR      = "__________"  # Name of what is plugged into outlet #4
WIDGET_WIDE  = 600           # Width of the "Outlet Timers" window
WIDGET_HIGH  = 400           # Height of the "Outlet Timers" window
OUTROW       = 0
DOORROW      = 10


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
        ## Define the MASTER for the window, and spawn the other two windows
        self.master = master
        self.newStatus = Toplevel(self.master)
        self.win1 = Status_Window(self.newStatus)
        self.newGraphs = Toplevel(self.master)
        self.win2 = Graphs_Window(self.newGraphs)

        ## Define the geometry and title for the control window
        self.master.geometry("{:d}x{:d}+0+{:d}".format(
            WIDGET_WIDE,WIDGET_HIGH,PI_TOOLBAR))
        self.master.title("Control Window")
        
        ## Initialize the various variables required
        self.ON1time = 0
        self.OFF1time = 0
        self.ON2time = 0
        self.OFF2time = 0
        self.ON3time = 0
        self.OFF3time = 0
        self.ON4time = 0
        self.OFF4time = 0
        self.var1 = BooleanVar()
        self.var2 = BooleanVar()
        self.var3 = BooleanVar()
        self.var4 = BooleanVar()
        self.ENABLE1 = False
        self.ENABLE2 = False
        self.ENABLE3 = False
        self.ENABLE4 = False
        self.changedState = False

        ## A "frame" holds the various GUI controls
        self.frame = Frame(self.master)
        self.frame.pack(expand=0)
        
        ## Create the labels and position them in a grid layout
        Label(self.frame, text='Switched Outlets', fg='darkblue',
              font=('courier', 14, 'bold')).grid(row=OUTROW, column=0,
                                                 columnspan=4)
        # Outlet #1
        Label(self.frame, text=OUT1STR+' (#1)').grid(row=OUTROW+1,column=0)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON1time),
              fg='green').grid(row=OUTROW+3,column=0)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF1time)
              , fg='red').grid(row=OUTROW+5,column=0)
        # Outlet #2
        Label(self.frame, text=OUT2STR+' (#2)').grid(row=OUTROW+1,column=1)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON2time),
              fg='green').grid(row=OUTROW+3,column=1)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF2time),
              fg='red').grid(row=OUTROW+5,column=1)
        # Outlet #3
        Label(self.frame, text=OUT3STR+' (#3)').grid(row=OUTROW+1,column=2)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON3time),
              fg='green').grid(row=OUTROW+3,column=2)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF3time),
              fg='red').grid(row=OUTROW+5,column=2)
        # Outlet #4
        Label(self.frame, text=OUT4STR+' (#4)').grid(row=OUTROW+1,column=3)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON4time),
              fg='green').grid(row=OUTROW+3,column=3)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF4time),
              fg='red').grid(row=OUTROW+5,column=3)
        
        ## Create an 'ENABLE' checkbox for each outlet
        self.EN1 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var1,
                               command=self.update1ENABLE)
        self.EN1.grid(row=OUTROW+2, column=0)
        self.EN2 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var2,
                               command=self.update2ENABLE)
        self.EN2.grid(row=OUTROW+2, column=1)
        self.EN3 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var3,
                               command=self.update3ENABLE)
        self.EN3.grid(row=OUTROW+2, column=2)
        self.EN4 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var4,
                               command=self.update4ENABLE)
        self.EN4.grid(row=OUTROW+2, column=3)
        
        ## Create the sliders and position them in a grid layout.
        ## The 'command' attribute specifies a method to call when
        ## a slider is moved
        # Outlet #1
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window
        self.S1ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update1ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S1ON.grid(row=OUTROW+4,column=0)
        self.S1OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update1OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S1OFF.grid(row=OUTROW+6,column=0)
        # Outlet #2
        self.S2ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update2ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S2ON.grid(row=OUTROW+4,column=1)
        self.S2OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update2OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S2OFF.grid(row=OUTROW+6,column=1)
        # Outlet #3
        self.S3ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update3ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S3ON.grid(row=OUTROW+4,column=2)
        self.S3OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update3OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S3OFF.grid(row=OUTROW+6,column=2)
        # Outlet #4
        self.S4ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update4ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S4ON.grid(row=OUTROW+4,column=3)
        self.S4OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update4OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S4OFF.grid(row=OUTROW+6,column=3)
        
        
        ## Temperature sliders...
        
        
        
        
        
        
        # ## Set up the 3 variable text display areas
        # # Current Time
        # self.disptime = Label(self.frame, font=('courier', 14, 'bold'),
        #                       fg='darkblue')
        # self.disptime.grid(row=6, column=0, columnspan=4)
        # # Status of the relays
        # self.disprelay = Label(self.frame, font=('courier', 14, 'bold'),
        #                        fg='darkgreen')
        # self.disprelay.grid(row=7, column=2, columnspan=2)
        # # Debugging information
        # self.disp = Label(self.frame, font=('courier', 14, 'bold'),
        #                   fg='darkred')
        # self.disp.grid(row=7, column=0, columnspan=2)

        
        
        
        
            ### The following methods are called whenever a checkbox is clicked:
    def update1ENABLE(self):
        self.ENABLE1 = self.var1.get()
        self.changedState = True

    def update2ENABLE(self):
        self.ENABLE2 = self.var2.get()
        self.changedState = True

    def update3ENABLE(self):
        self.ENABLE3 = self.var3.get()
        self.changedState = True

    def update4ENABLE(self):
        self.ENABLE4 = self.var4.get()
        self.changedState = True
    
    
    ### The following methods are called whenever a slider is moved:
    def update1ON(self,seltime):
        self.ON1time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON1time),
              fg='green').grid(row=2,column=0)
        self.changedState = True
        
    def update1OFF(self,seltime):
        self.OFF1time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF1time),
              fg='red').grid(row=4,column=0)
        self.changedState = True
        
    def update2ON(self,seltime):
        self.ON2time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON2time),
              fg='green').grid(row=2,column=1)
        self.changedState = True
        
    def update2OFF(self,seltime):
        self.OFF2time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF2time),
              fg='red').grid(row=4,column=1)
        self.changedState = True

    def update3ON(self,seltime):
        self.ON3time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON3time),
              fg='green').grid(row=2,column=2)
        self.changedState = True
        
    def update3OFF(self,seltime):
        self.OFF3time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF3time),
              fg='red').grid(row=4,column=2)
        self.changedState = True
        
    def update4ON(self,seltime):
        self.ON4time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON4time),
              fg='green').grid(row=2,column=3)
        self.changedState = True
        
    def update4OFF(self,seltime):
        self.OFF4time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF4time),
              fg='red').grid(row=4,column=3)
        self.changedState = True

        
    ### This method makes the string for display of time above slider bar
    def makeStringTime(self,inTime):
        minute = 60 * (inTime % 1)      # Compute minutes from decimal hour
        if inTime == 24:                # Catch case of 24:00
            inTime = 0
        if inTime >= 12:                # Set PM/AM times
            ampm = "PM"
            inTime -= 12
        else:
            ampm = "AM"
        if int(inTime) == 0:            # Catch case of 0:00
            inTime = 12
        return "{:2d}:{:0>2d} {:s}".format(int(inTime),int(minute),ampm)



        
        
        
    def update(self):
        """
        update: method for updating the display windows
        """
        self.win1.update()
        self.frame.after(5000, self.update)
        


