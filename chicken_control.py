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
__copyright__ = 'Copyright 2019-2021, chicken-pi'
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
WIDGET_WIDE  = 600           # Width of the "Control Window"
WIDGET_HIGH  = 400           # Height of the "Control Window"
OUTROW       = 0
DOORROW      = 14
CONTBG       = 'lightgreen'


class ControlWindow():
    """
    ControlWindow class
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
        self.win1 = StatusWindow(self.newStatus, WIDGET_WIDE)
        self.newGraphs = Toplevel(self.master, bg='forestgreen')
        self.win2 = GraphsWindow(self.newGraphs)

        ## Define the geometry and title for the control window
        self.master.geometry(f"{WIDGET_WIDE}x{WIDGET_HIGH}+0+{PI_TOOLBAR}")
        self.master.title("Control Window")
        self.master.configure(bg=CONTBG)

        ## A "frame" holds the various GUI controls
        self.frame = Frame(self.master)
        self.frame.pack(expand=1, fill=BOTH)
        
        ## Initialize the various variables required
        self.ENABLE  = [False]*5    # Switch / Door Enabled
        self.ANDOR   = [False]*4    # Time AND/OR Temperature
        self.ONtime  = [0]*5        # Switch / Door turn on time
        self.OFFtime = [0]*5        # Switch / Door turn off time
        self.SWCHtmp =  [20]*5      # Temp / Light trigger for switch / door
        self.TD      = [0]*4        # Temperature direction for trigger
        # Variables needed for ENABLE boxes
        self.var = [BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar()]
        # Variables needed for temp radio buttons
        self.vara = [IntVar(), IntVar(), IntVar(), IntVar()]
        self.varb = [BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar()]
        self.vard = BooleanVar()    # Variable needed for door enable
        self.changedState = False   # Trigger for updating relay state
        self.nupdate = 0            # Keep a running count of update cycles
        

        ### SWITCHED OUTLETS
        outlet = []
        names = [OUT1STR, OUT2STR, OUT3STR, OUT4STR]
        for i, name in enumerate(names):
            outlet.append(OutletControl(self.frame, name, i))

        ### DOOR
        door = DoorControl(self.frame)      
    

    ### Update Method ###
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



class OutletControl():
    """Outlet Control Class
    
    """

    def __init__(self, frame, name, column):
        """Initialize Class

        Inputs:
          frame:
          name:
          column:
        """
        # Set change state
        self.changedState = False

        ## Initialize the various variables required
        self.ENABLE  = False        # Switch Enabled
        self.ANDOR   = False        # Time AND/OR Temperature
        self.ONtime  = 0            # Switch turn on time
        self.OFFtime = 0            # Switch turn off time
        self.SWCHtmp = 20           # Temp / Light trigger for switch
        self.TD      = 0            # Temperature direction for trigger
        self.en_var = BooleanVar()  # Variable needed for ENABLE boxes
        self.int_var = IntVar()     # Variables needed for temp radio button
        self.bool_var = BooleanVar()

        # Column Label for this outlet
        Label(frame, text=f"{name} (#{column+1})",
            bg='#f0f0f0').grid(row=OUTROW+1, column=column, sticky=W+E)

        # Individual Labels:
        self.onLabel = Label(frame, fg='green', bg='#e0ffe0',
                             text=f" ON {make_string_time(self.ONtime)}")
        self.offLabel = Label(frame, fg='red', bg='#ffe0e0',
                              text=f" OFF {make_string_time(self.OFFtime)}")
        self.tmpLabel = Label(frame, fg='blue', bg='#e0e0ff',
                      text=f" Coop Temp {make_string_temp(self.SWCHtmp)}")

        # Enable Box
        self.enableBox = Checkbutton(frame, text='Enable', variable=self.en_var, 
                                     command=self.update_enable, onvalue=True, 
                                     offvalue=False)

        # Sliders
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window

        self.onSlider = Scale(frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                              resolution=0.25, command=self.update_on_time, 
                              variable=DoubleVar, length=slider_size, showvalue=0, 
                              troughcolor='#bfd9bf')
        self.offSlider = Scale(frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                               resolution=0.25, command=self.update_off_time, 
                               variable=DoubleVar, length=slider_size, showvalue=0, 
                               troughcolor='#d9bfbf')
        self.tmpSlider = Scale(frame, from_=20, to=80, digits=2, orient=HORIZONTAL,
                               resolution=5, command=self.update_temp_trigger, 
                               variable=IntVar, length=slider_size, showvalue=0, 
                               troughcolor='#bfbfd9')
           
        # AND/OR Buttons
        self.andorFrame = Frame(frame)
        self.andButton = Radiobutton(self.andorFrame, indicatoron=0, value=True,
                                     text='   AND   ', variable=self.bool_var,
                                     command=self.update_andor, bg='#c0c0c0', 
                                     selectcolor='#ffaa00')
        self.orButton = Radiobutton(self.andorFrame, indicatoron=0, value=False,
                                    text='   OR   ', variable=self.bool_var,
                                    command=self.update_andor, bg='#c0c0c0', 
                                    selectcolor='#ffaa00')

        # Temperature Direction Radio Buttons
        self.noTempButton = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=0,
                                        command=self.update_temp_direction, 
                                        variable=self.int_var, anchor=W,
                                        text='Temp independent', font=('',9))
        self.upTempButton = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=1,
                                        command=self.update_temp_direction, 
                                        variable=self.int_var, anchor=W,
                                        text='Turn ON above: ')
        self.dnTempButton = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=-1,
                                        command=self.update_temp_direction, 
                                        variable=self.int_var, anchor=W,
                                        text='Turn ON below:')

        # Set everything to the grid
        self.onLabel.grid(row=OUTROW+3, column=column, sticky=W+E)
        self.offLabel.grid(row=OUTROW+5, column=column, sticky=W+E)
        self.tmpLabel.grid(row=OUTROW+11, column=column, sticky=W+E)
        self.enableBox.grid(row=OUTROW+2, column=column)
        self.onSlider.grid(row=OUTROW+4, column=column, sticky=W+E)
        self.offSlider.grid(row=OUTROW+6, column=column, sticky=W+E)
        self.tmpSlider.grid(row=OUTROW+12, column=column, sticky=W+E)
        self.andorFrame.grid(row=OUTROW+7, column=column, sticky=W+E)
        self.andButton.pack(side=LEFT, expand=1)
        self.orButton.pack(side=LEFT, expand=1)
        self.noTempButton.grid(row=OUTROW+8, column=column, sticky=W+E)
        self.upTempButton.grid(row=OUTROW+9, column=column, sticky=W+E)
        self.dnTempButton.grid(row=OUTROW+10, column=column, sticky=W+E)

    # Various Update Methods
    def update_enable(self):
        self.ENABLE = self.en_var.get()
        self.changedState = True
        print(self.ENABLE)

    def update_on_time(self, seltime):
        self.ONtime = float(seltime)
        self.onLabel.config(text=f" ON {make_string_time(self.ONtime)}")
        self.changedState = True
        print(self.ONtime)
    
    def update_off_time(self,seltime):
        self.OFFtime = float(seltime)
        self.offLabel.config(text=f" OFF {make_string_time(self.OFFtime)}")
        self.changedState = True
        print(self.OFFtime)
        
    def update_temp_trigger(self,seltemp):
        self.SWCHtmp = int(seltemp)
        self.tmpLabel.config(text=f" Coop Temp {make_string_temp(self.SWCHtmp)}")
        self.changedState = True
        print(self.SWCHtmp)

    def update_andor(self):
        self.ANDOR = self.bool_var.get()
        self.changedState = True
        print(self.ANDOR)

    def update_temp_direction(self):
        self.TD = self.int_var.get()
        self.changedState = True
        print(self.TD)



class DoorControl():
    """Door Control Class
    
    """

    def __init__(self, frame):
        """Initialize Class

        Inputs:
          frame:
        """
        # Set change state
        self.changedState = False

        ## Initialize the various variables required
        self.ENABLE  = False        # Switch Enabled
        self.ANDOR   = False        # Time AND/OR Temperature
        self.ONtime  = 0            # Switch turn on time
        self.OFFtime = 0            # Switch turn off time
        self.SWCHtmp = 20           # Temp / Light trigger for switch
        self.TD      = 0            # Temperature direction for trigger
        self.en_var = BooleanVar()  # Variable needed for ENABLE boxes
        self.int_var = IntVar()     # Variables needed for temp radio button
        self.bool_var = BooleanVar()
        
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window

        ## Create the labels
        Label(frame, text=' - '*40,fg='darkblue').grid(
            row=DOORROW-1, column=0, columnspan=4, sticky=W+E)
        Label(frame, text='Automated Chicken Door', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=DOORROW, column=0, columnspan=4, sticky=W+E)

        # Column 0: ENABLE
        self.doorEnable = Checkbutton(frame, text='Enable', onvalue=True,
                                      offvalue=False, variable=self.en_var,
                                      command=self.update_door_enable)
        
        # Column 1: Open Time
        self.doorOpenLabel = Label(frame, fg='green', bg='#e0ffe0',
                                   text=f" OPEN {make_string_time(self.ONtime)}")
        self.doorOpenSlider = Scale(frame, from_=0, to=24, digits=4,
                                    orient=HORIZONTAL, resolution=0.25,
                                    command=self.update_door_open, showvalue=0,
                                    variable=DoubleVar, length=slider_size,
                                    troughcolor='#bfd9bf')
        
        # Column 2: Close Time
        self.doorCloseLabel = Label(frame, fg='red', bg='#ffe0e0',
                                    text=f" CLOSE {make_string_time(self.OFFtime)}")
        self.doorCloseSlider = Scale(frame, from_=0, to=24, digits=4,
                                     orient=HORIZONTAL, resolution=0.25,
                                     command=self.update_door_close,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#d9bfbf')
        
        # Column 3: Light Trigger
        self.SWCHtmp = 2
        self.doorLightLabel = Label(frame, fg='#9932cc', bg='#f3e6f9',
                                    text=f" LIGHT {make_string_light(self.SWCHtmp)}")
        self.doorLightSlider = Scale(frame, from_=2, to=4, digits=4,
                                     orient=HORIZONTAL, resolution=0.05,
                                     command=self.update_door_light,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#cfc4d4')
        
        # Set everything to the grid
        self.doorEnable.grid(row=DOORROW+1, column=0, rowspan=2)
        self.doorOpenLabel.grid(row=DOORROW+1, column=1, sticky=W+E)
        self.doorOpenSlider.grid(row=DOORROW+2, column=1, sticky=W+E)
        self.doorCloseLabel.grid(row=DOORROW+1, column=2, sticky=W+E)
        self.doorCloseSlider.grid(row=DOORROW+2, column=2, sticky=W+E)
        self.doorLightLabel.grid(row=DOORROW+1, column=3, sticky=W+E)
        self.doorLightSlider.grid(row=DOORROW+2, column=3, sticky=W+E)
        
    # Various Update Methods
    def update_door_enable(self):
        self.ENABLE = self.en_var.get()
        self.changedState = True
        print(self.ENABLE)

    def update_door_open(self, seltime):
        self.ONtime = float(seltime)
        self.doorOpenLabel.config(text=f" OPEN {make_string_time(self.ONtime)}")
        self.changedState = True
        print(self.ONtime)

    def update_door_close(self, seltime):
        self.OFFtime = float(seltime)
        self.doorCloseLabel.config(text=f" CLOSE {make_string_time(self.OFFtime)}")
        self.changedState = True
        print(self.OFFtime)
        
    def update_door_light(self, seltime):
        self.SWCHtmp = float(seltime)
        self.doorLightLabel.config(text=f" LIGHT {make_string_light(self.SWCHtmp)}")
        self.changedState = True
        print(self.SWCHtmp)

 

### This method makes the string for display of time above slider bar
def make_string_time(inTime):
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
    return f"{int(inTime):2d}:{int(minute):0>2d} {ampm}"

### This method makes the string for display of temperature above slider bar
def make_string_temp(inTemp):
    return f"{int(inTemp):2d}\N{DEGREE SIGN} F"

### This method makes the string for display of light level above slider bar
def make_string_light(inLogLux):
    inLux = 10 ** inLogLux
    if inLux < 1000:                         # Round to make look pretty
        inLux = np.round(inLux / 10.) * 10.
    else:
        inLux = np.round(inLux / 100.) * 100.
    return f"{int(inLux):,.0f} lux"
 