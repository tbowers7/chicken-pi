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
CONTBG       = 'lightgreen'


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
        self.newGraphs = Toplevel(self.master, bg='forestgreen')
        self.win2 = Graphs_Window(self.newGraphs)

        ## Define the geometry and title for the control window
        self.master.geometry("{:d}x{:d}+0+{:d}".format(
            WIDGET_WIDE,WIDGET_HIGH,PI_TOOLBAR))
        self.master.title("Control Window")
        self.master.configure(bg=CONTBG)

        ## A "frame" holds the various GUI controls
        self.frame = Frame(self.master)
        self.frame.pack(expand=0)
        
        ## Initialize the various variables required
        self.ENABLE = [False]*4     # Switch Enabled
        self.ONtime = [0]*4         # Switch turn on time
        self.OFFtime = [0]*4        # Switch turn off time
        self.SWCHtmp =  [20]*4      # Temperature trigger for switch
        self.TD = [0]*4             # Temperature direction for trigger
        # Variables needed for ENABLE boxes
        self.var = [BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar()]
        # Variables needed for temp radio buttons
        self.vara = [IntVar(), IntVar(), IntVar(), IntVar()]
        self.changedState = False   # Trigger for updating relay state
        self.nupdate = 0            # Keep a running count of update cycles
        
        
        ## Create the labels and position them in a grid layout
        Label(self.frame, text='Switched Outlets', fg='darkblue',
              font=('courier', 14, 'bold')).grid(row=OUTROW, column=0,
                                                 columnspan=4)
        
        self.onLabels  = []
        self.offLabels = []
        self.tmpLabels = []
        outlets = range(4)
        strs    = [OUT1STR, OUT2STR, OUT3STR, OUT4STR]
        
        for (i, s, ont, offt, swt) in zip(
                outlets, strs, self.ONtime, self.OFFtime, self.SWCHtmp):
            # Column Label for this outlet
            Label(self.frame, text=s+' (#{:d})'.format(i+1)).grid(
                row=OUTROW+1, column=i)
            # Individual Labels:
            self.onLabels.append(Label(self.frame, fg='green', text=' ON '+
                                       self.make_string_time(ont)))
            self.offLabels.append(Label(self.frame, fg='red', text=' OFF '+
                                        self.make_string_time(offt)))
            self.tmpLabels.append(Label(self.frame, fg='blue',
                                        text=' Temperature '+
                                        self.make_string_temp(swt)))
            # Set to grid
            self.onLabels[i].grid(row=OUTROW+3, column=i)
            self.offLabels[i].grid(row=OUTROW+5, column=i)
            self.tmpLabels[i].grid(row=OUTROW+10, column=i)
            
            
        ## Create an 'ENABLE' checkbox for each outlet
        self.enableBox = []
        cmds = [self.update_enable_1, self.update_enable_2,
                self.update_enable_3, self.update_enable_4]
        
        for (i, cmd, v) in zip(outlets, cmds, self.var):
            self.enableBox.append(Checkbutton(self.frame, text='Enable',
                                              onvalue=True, offvalue=False,
                                              variable=v, command=cmd))
            self.enableBox[i].grid(row=OUTROW+2, column=i)
            
            
        ## Create the sliders and position them in a grid layout.
        ## The 'command' attribute specifies a method to call when
        ## a slider is moved
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window
        
        self.onSlider = []
        self.offSlider = []
        self.tmpSlider = []
        oncmds  = [self.update_on_1, self.update_on_2,
                   self.update_on_3, self.update_on_4]
        offcmds = [self.update_off_1, self.update_off_2,
                   self.update_off_3, self.update_off_4]
        tmpcmds = [self.update_temp_1, self.update_temp_2,
                   self.update_temp_3, self.update_temp_4]
        
        for (i, onc, offc, tmpc) in zip(outlets, oncmds, offcmds, tmpcmds):
            self.onSlider.append(Scale(self.frame, from_=0, to=24, digits=4,
                                       orient=HORIZONTAL, resolution=0.25,
                                       command=onc, variable=DoubleVar,
                                       length=slider_size, showvalue=0))
            self.offSlider.append(Scale(self.frame, from_=0, to=24, digits=4,
                                       orient=HORIZONTAL, resolution=0.25,
                                       command=offc, variable=DoubleVar,
                                        length=slider_size, showvalue=0))
            self.tmpSlider.append(Scale(self.frame, from_=20, to=80, digits=2,
                                        orient=HORIZONTAL, resolution=5,
                                        command=tmpc, variable=IntVar,
                                        length=slider_size, showvalue=0))
            # Set to grid
            self.onSlider[i].grid(row=OUTROW+4, column=i)
            self.offSlider[i].grid(row=OUTROW+6, column=i)
            self.tmpSlider[i].grid(row=OUTROW+11, column=i)
            
        
        
        ## Create radio buttons for temp and position them in a grid layout.
        self.noTempButton = []
        self.upTempButton = []
        self.dnTempButton = []

        radiocmds = [self.update_tempdir_1, self.update_tempdir_2,
                     self.update_tempdir_3, self.update_tempdir_4]

        for (i, cmd) in zip(outlets, radiocmds):
            self.noTempButton.append(Radiobutton(self.frame, fg='blue', value=0,
                                                 variable=self.vara[i],
                                                 text='Temp independent',
                                                 command=cmd,
                                                 font=('',9)))
            self.upTempButton.append(Radiobutton(self.frame, fg='blue', value=1,
                                                 variable=self.vara[i],
                                                 text='Turn ON above: ',
                                                 command=cmd))
            self.dnTempButton.append(Radiobutton(self.frame, fg='blue',value=-1,
                                                 variable=self.vara[i],
                                                 text='Turn OFF above:',
                                                 command=cmd))
            # Set to grid
            self.noTempButton[i].grid(row=OUTROW+7, column=i)
            self.upTempButton[i].grid(row=OUTROW+8, column=i)
            self.dnTempButton[i].grid(row=OUTROW+9, column=i)
        
        
        
        
        
        
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
    def update_enable(self, i):
        self.ENABLE[i] = self.var[i].get()
        self.changedState = True
        #print(self.ENABLE)
            
    # Helper functions
    def update_enable_1(self):
        self.update_enable(0)

    def update_enable_2(self):
        self.update_enable(1)

    def update_enable_3(self):
        self.update_enable(2)

    def update_enable_4(self):
        self.update_enable(3)
    
    
    ### The following methods are called whenever a slider is moved:
    def update_on_time(self, seltime, i):
        self.ONtime[i] = float(seltime)
        self.onLabels[i].config(text=' ON '+
                                self.make_string_time(self.ONtime[i]))
        self.changedState = True
        #print(self.ONtime)
    
    def update_off_time(self,seltime, i):
        self.OFFtime[i] = float(seltime)
        self.offLabels[i].config(text=' OFF '+
                                 self.make_string_time(self.OFFtime[i]))
        self.changedState = True
        #print(self.OFFtime)
        
    def update_temp_trigger(self,seltemp, i):
        self.SWCHtmp[i] = int(seltemp)
        self.tmpLabels[i].config(text=' Temperature '+
                                 self.make_string_temp(self.SWCHtmp[i]))
        self.changedState = True
        #print(self.SWCHtmp)

    # Helper functions
    def update_on_1(self,seltime):
        self.update_on_time(seltime, 0)
        
    def update_on_2(self,seltime):
        self.update_on_time(seltime, 1)
        
    def update_on_3(self,seltime):
        self.update_on_time(seltime, 2)
        
    def update_on_4(self,seltime):
        self.update_on_time(seltime, 3)
        
    def update_off_1(self, seltime):
        self.update_off_time(seltime, 0)
        
    def update_off_2(self,seltime):
        self.update_off_time(seltime, 1)

    def update_off_3(self,seltime):
        self.update_off_time(seltime, 2)
        
    def update_off_4(self,seltime):
        self.update_off_time(seltime, 3)

    def update_temp_1(self, seltemp):
        self.update_temp_trigger(seltemp, 0)
        
    def update_temp_2(self,seltemp):
        self.update_temp_trigger(seltemp, 1)
        
    def update_temp_3(self,seltemp):
        self.update_temp_trigger(seltemp, 2)
        
    def update_temp_4(self,seltemp):
        self.update_temp_trigger(seltemp, 3)
    
    
    ### The following methods are called whenever a radio button is clicked:
    def update_temp_direction(self, i):
        self.TD[i] = self.vara[i].get()
        self.changedState = True
        #print(self.TD)
        
    # Helper functions
    def update_tempdir_1(self):
        self.update_temp_direction(0)
        
    def update_tempdir_2(self):
        self.update_temp_direction(1)
        
    def update_tempdir_3(self):
        self.update_temp_direction(2)
        
    def update_tempdir_4(self):
        self.update_temp_direction(3)
        
    
    
    ### This method makes the string for display of time above slider bar
    def make_string_time(self,inTime):
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

    ### This method makes the string for display of temperature above slider bar
    def make_string_temp(self,inTemp):
        return "{:2d}\N{DEGREE SIGN} F".format(int(inTemp))



        
        
        
    def update(self):
        """
        update: method for updating the display windows
        """
        self.nupdate += 1
        self.win1.update()
        print(self.nupdate)
        if (self.nupdate % 5) == 0:
            self.win2.update()
        print("Waiting for next call...")
        self.master.after(5000, self.update)
        


