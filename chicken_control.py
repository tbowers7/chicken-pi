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
WIDGET_WIDE  = 600           # Width of the "Control Window"
WIDGET_HIGH  = 400           # Height of the "Control Window"
OUTROW       = 0
DOORROW      = 14
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
        self.win1 = Status_Window(self.newStatus, WIDGET_WIDE)
        self.newGraphs = Toplevel(self.master, bg='forestgreen')
        self.win2 = Graphs_Window(self.newGraphs)

        ## Define the geometry and title for the control window
        self.master.geometry("{:d}x{:d}+0+{:d}".format(
            WIDGET_WIDE,WIDGET_HIGH,PI_TOOLBAR))
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
        ## Create the labels and position them in a grid layout
        Label(self.frame, text='Switched Outlets', fg='darkblue', bg='#ffff80',
              font=('courier', 14, 'bold')).grid(row=OUTROW, column=0,
                                                 columnspan=4, sticky=W+E)
        
        self.onLabels  = []
        self.offLabels = []
        self.tmpLabels = []
        outlets = range(4)
        strs    = [OUT1STR, OUT2STR, OUT3STR, OUT4STR]
        
        for (i, s, ont, offt, swt) in zip(
                outlets, strs, self.ONtime, self.OFFtime, self.SWCHtmp):
            # Column Label for this outlet
            Label(self.frame, text=s+' (#{:d})'.format(i+1),
                  bg='#f0f0f0').grid(row=OUTROW+1, column=i, sticky=W+E)
            # Individual Labels:
            self.onLabels.append(
                Label(self.frame, fg='green', bg='#e0ffe0',
                      text=' ON '+self.make_string_time(ont)))
            self.offLabels.append(
                Label(self.frame, fg='red', bg='#ffe0e0',
                      text=' OFF '+self.make_string_time(offt)))
            self.tmpLabels.append(
                Label(self.frame, fg='blue', bg='#e0e0ff',
                      text=' Temperature '+self.make_string_temp(swt)))
            # Set to grid
            self.onLabels[i].grid(row=OUTROW+3, column=i, sticky=W+E)
            self.offLabels[i].grid(row=OUTROW+5, column=i, sticky=W+E)
            self.tmpLabels[i].grid(row=OUTROW+11, column=i, sticky=W+E)
            
            
        ## Create an 'ENABLE' checkbox for each outlet
        self.enableBox = []
        cmds = [self.update_enable_1, self.update_enable_2,
                self.update_enable_3, self.update_enable_4]
        
        for (i, cmd, v) in zip(outlets, cmds, self.var):
            self.enableBox.append(
                Checkbutton(self.frame, text='Enable', variable=v, command=cmd,
                            onvalue=True, offvalue=False))
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
            self.onSlider.append(
                Scale(self.frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                      resolution=0.25, command=onc, variable=DoubleVar,
                      length=slider_size, showvalue=0, troughcolor='#bfd9bf'))
            self.offSlider.append(
                Scale(self.frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                      resolution=0.25, command=offc, variable=DoubleVar,
                      length=slider_size, showvalue=0, troughcolor='#d9bfbf'))
            self.tmpSlider.append(
                Scale(self.frame, from_=20, to=80, digits=2, orient=HORIZONTAL,
                      resolution=5, command=tmpc, variable=IntVar,
                      length=slider_size, showvalue=0, troughcolor='#bfbfd9'))
            # Set to grid
            self.onSlider[i].grid(row=OUTROW+4, column=i, sticky=W+E)
            self.offSlider[i].grid(row=OUTROW+6, column=i, sticky=W+E)
            self.tmpSlider[i].grid(row=OUTROW+12, column=i, sticky=W+E)
        
        
        ## Create AND/OR radio buttons for choosing time AND/OR temperature
        self.andButton = []
        self.orButton  = []
        self.andorFrame = []
        
        andorcmds = [self.update_andor_1, self.update_andor_2,
                     self.update_andor_3, self.update_andor_4]

        for (i, cmd) in zip(outlets, andorcmds):
            self.andorFrame.append(Frame(self.frame))
            self.andorFrame[i].grid(row=OUTROW+7, column=i, sticky=W+E)
            
            self.andButton.append(
                Radiobutton(self.andorFrame[i], indicatoron=0, value=True,
                            text='   AND   ', variable=self.varb[i],
                            command=cmd, bg='navajowhite', selectcolor='blue'))
            self.orButton.append(
                Radiobutton(self.andorFrame[i], indicatoron=0, value=False,
                            text='   OR   ', variable=self.varb[i],
                            command=cmd, bg='navajowhite', selectcolor='blue'))
            # Set to grid
            self.andButton[i].pack(side=LEFT, expand=1)
            self.orButton[i].pack(side=LEFT, expand=1)
        
        
        ## Create radio buttons for temp and position them in a grid layout.
        self.noTempButton = []
        self.upTempButton = []
        self.dnTempButton = []

        radiocmds = [self.update_tempdir_1, self.update_tempdir_2,
                     self.update_tempdir_3, self.update_tempdir_4]

        for (i, cmd) in zip(outlets, radiocmds):
            self.noTempButton.append(
                Radiobutton(self.frame, fg='blue', bg='#f0f0ff', value=0,
                            command=cmd, variable=self.vara[i],
                            text='Temp independent', font=('',9), anchor=W))
            self.upTempButton.append(
                Radiobutton(self.frame, fg='blue', bg='#f0f0ff', value=1,
                            command=cmd, variable=self.vara[i],
                            text='Turn ON above: ', anchor=W))
            self.dnTempButton.append(
                Radiobutton(self.frame, fg='blue', bg='#f0f0ff', value=-1,
                            command=cmd, variable=self.vara[i],
                            text='Turn ON below:', anchor=W))
            # Set to grid
            self.noTempButton[i].grid(row=OUTROW+8, column=i, sticky=W+E)
            self.upTempButton[i].grid(row=OUTROW+9, column=i, sticky=W+E)
            self.dnTempButton[i].grid(row=OUTROW+10, column=i, sticky=W+E)
        
        
        ### DOOR
        ## Create the labels
        Label(self.frame, text=' - '*40,fg='darkblue').grid(
            row=DOORROW-1, column=0, columnspan=4, sticky=W+E)
        Label(self.frame, text='Automated Chicken Door', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=DOORROW, column=0, columnspan=4, sticky=W+E)

        # Column 0: ENABLE
        self.doorEnable = Checkbutton(self.frame, text='Enable', onvalue=True,
                                      offvalue=False, variable=self.vard,
                                      command=self.update_door_enable)
        self.doorEnable.grid(row=DOORROW+1, column=0, rowspan=2)
        
        # Column 1: Open Time
        self.doorOpenLabel = Label(self.frame, fg='green', bg='#e0ffe0',
                                   text=' OPEN '+
                                   self.make_string_time(self.ONtime[4]))
        self.doorOpenSlider = Scale(self.frame, from_=0, to=24, digits=4,
                                    orient=HORIZONTAL, resolution=0.25,
                                    command=self.update_door_open, showvalue=0,
                                    variable=DoubleVar, length=slider_size,
                                    troughcolor='#bfd9bf')
        self.doorOpenLabel.grid(row=DOORROW+1, column=1, sticky=W+E)
        self.doorOpenSlider.grid(row=DOORROW+2, column=1, sticky=W+E)
        
        # Column 2: Close Time
        self.doorCloseLabel = Label(self.frame, fg='red', bg='#ffe0e0',
                                    text=' CLOSE '+
                                    self.make_string_time(self.OFFtime[4]))
        self.doorCloseSlider = Scale(self.frame, from_=0, to=24, digits=4,
                                     orient=HORIZONTAL, resolution=0.25,
                                     command=self.update_door_close,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#d9bfbf')
        self.doorCloseLabel.grid(row=DOORROW+1, column=2, sticky=W+E)
        self.doorCloseSlider.grid(row=DOORROW+2, column=2, sticky=W+E)
        
        # Column 3: Light Trigger
        self.SWCHtmp[4] = 2
        self.doorLightLabel = Label(self.frame, fg='#9932cc', bg='#f3e6f9',
                                    text=' LIGHT '+
                                    self.make_string_light(self.SWCHtmp[4]))
        self.doorLightSlider = Scale(self.frame, from_=2, to=4, digits=4,
                                     orient=HORIZONTAL, resolution=0.05,
                                     command=self.update_door_light,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#cfc4d4')
        self.doorLightLabel.grid(row=DOORROW+1, column=3, sticky=W+E)
        self.doorLightSlider.grid(row=DOORROW+2, column=3, sticky=W+E)
        
        
        
        
        
        
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
    
    
    ### The following methods are called whenever an AND/OR button is clicked:
    def update_andor(self, i):
        self.ANDOR[i] = self.varb[i].get()
        self.changedState = True
        print(self.ANDOR)
        
    # Helper functions
    def update_andor_1(self):
        self.update_andor(0)
    
    def update_andor_2(self):
        self.update_andor(1)
    
    def update_andor_3(self):
        self.update_andor(2)
    
    def update_andor_4(self):
        self.update_andor(3)
    
    
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
    
    
    ### The following methods are called whenever door options change:
    def update_door_enable(self):
        self.ENABLE[4] = self.vard.get()
        self.changedState = True
        #print(self.ENABLE)

    def update_door_open(self, seltime):
        self.ONtime[4] = float(seltime)
        self.doorOpenLabel.config(text=' OPEN '+
                                  self.make_string_time(self.ONtime[4]))
        self.changedState = True
        #print(self.ONtime)

    def update_door_close(self, seltime):
        self.OFFtime[4] = float(seltime)
        self.doorCloseLabel.config(text=' CLOSE '+
                                  self.make_string_time(self.OFFtime[4]))
        self.changedState = True
        #print(self.OFFtime)
        
    def update_door_light(self, seltime):
        self.OFFtime[4] = float(seltime)
        self.doorLightLabel.config(text=' LIGHT '+
                                   self.make_string_light(self.OFFtime[4]))
        self.changedState = True
        #print(self.OFFtime)

       
    
    
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

    ### This method makes the string for display of light level above slider bar
    def make_string_light(self,inLogLux):
        inLux = 10 ** inLogLux
        if inLux < 1000:                         # Round to make look pretty
            inLux = np.round(inLux / 10.) * 10.
        else:
            inLux = np.round(inLux / 100.) * 100.
        return "{:,.0f} lux".format(int(inLux))
    
    
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
