# -*- coding: utf-8 -*-

"""
  FILE: chicken_control.py

Control window, with all the shiny knobs and buttons

"""

# Futures
# […]

# Built-in/Generic Imports
from tkinter import *      # Tk for display window
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
try:
    from chicken_device import *
except:
    pass    # Allow pass for testing not on a RPi

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
OUTROW       = 1
DOORROW      = OUTROW + 14 + 1
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
        self.use_nws = False
        # Try/Except to allow for testing not on a RPi
        try:
            self.sensors = set_up_sensors()
            self.relays = Relay()
        except:
            self.sensors = setup_dummy_sensor()
            self.relays = DummyRelay()


        ## Define the MASTER for the window, and spawn the other two windows
        self.master = master
        self.newStatus = Toplevel(self.master)
        self.win1 = StatusWindow(self.newStatus, WIDGET_WIDE)
        if self.use_nws:
            self.newGraphs = Toplevel(self.master, bg='forestgreen')
            self.win2 = GraphsWindow(self.newGraphs)

        ## Define the geometry and title for the control window
        self.master.geometry(f"{WIDGET_WIDE}x{WIDGET_HIGH}+0+{PI_TOOLBAR}")
        self.master.title("Control Window")
        self.master.configure(bg=CONTBG)

        ## A "frame" holds the various GUI controls
        self.frame = Frame(self.master)
        self.frame.pack(expand=1, fill=BOTH)


        #===== SWITCHED OUTLETS =====#
        Label(self.frame, text='Relay-Controlled Outlets', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=OUTROW-1, column=0, columnspan=4, sticky=W+E)

        self.outlet = []
        for i, name in enumerate([OUT1STR, OUT2STR, OUT3STR, OUT4STR]):
            self.outlet.append(OutletControl(self.frame, name, i, self.sensors))

        #===== DOOR =====#
        Label(self.frame, text=' - '*40,fg='darkblue').grid(
            row=DOORROW-1, column=0, columnspan=4, sticky=W+E)
        Label(self.frame, text='Automated Chicken Door', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=DOORROW, column=0, columnspan=4, sticky=W+E)

        self.door = DoorControl(self.frame)
    
    def set_relays(self):
        pass


    ### Update Method ###
    def update(self):
        """
        update: method for updating the display windows
        """

        # This is the official time for Chicken Pi
        now = datetime.datetime.now()

        # Update status window on 0.5s cadence
        self.win1.update(now, self.sensors, self.outlet)

        # Update the NWS Graph window, if enableed
        if self.use_nws:
            self.win2.update(now)

        # Update the command tags in the Control Window
        for o in self.outlet:
            o.cmdTxt.configure(text=f"CMD: {o.state}")
        
        # Every 15 seconds, write changes in relay comand to relays
        if now.second % 15 == 0:
            self.set_relays()

        # Wait 0.5 seconds and repeat
        self.master.after(500, self.update)



class _BaseControl():
    """Base class for Object Control

    """

    def __init__(self):
        """Initialize Class

        """
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
        self.TimeCycle = 0          # Time cycle: ON or ON-OFF-ON or OFF-ON-OFF

    # Various Update Methods
    def update_enable(self):
        self.ENABLE = self.en_var.get()

    def update_on_time(self, seltime):
        self.ONtime = float(seltime)
        self.onLabel.config(text=f" ON {self.string_time(self.ONtime)}")
        self.update_time_cycle()

    def update_off_time(self, seltime):
        self.OFFtime = float(seltime)
        self.offLabel.config(text=f" OFF {self.string_time(self.OFFtime)}")
        self.update_time_cycle()

    def update_time_cycle(self):
        if self.ONtime == self.OFFtime or abs(self.ONtime - self.OFFtime) == 24:
            self.TimeCycle = 0                    # ON always
        elif self.ONtime > self.OFFtime:
            self.TimeCycle = 1                    # ON - OFF - ON
        else:
            self.TimeCycle = 2                    # OFF - ON - OFF

    ### This method makes the string for display of time above slider bar
    def string_time(self,inTime):
        hour, minute = (int(inTime), 60 * (inTime % 1)) # Compute minutes from inTime
        hour = 0 if hour == 24 else hour                # Catch case of 24:00
        ampm = "PM" if hour >= 12 else "AM"             # Set PM/AM times
        if hour >= 12:
            hour -= 12
        hour = 12 if hour == 0 else hour                # Catch case of 0:00
        return f"{hour:2d}:{int(minute):0>2d} {ampm}"

    ### This method makes the string for display of temperature above slider bar
    def string_temp(self,inTemp):
        return f"{int(inTemp):2d}\N{DEGREE SIGN} F"

    ### This method makes the string for display of light level above slider bar
    def string_light(self,inLogLux):
        inLux = 10 ** inLogLux
        # Round to make look pretty
        inLux = np.round(inLux / 10.) * 10. if inLux < 1000 else \
            np.round(inLux / 100.) * 100.
        return f"{inLux:,.0f} lux"




class OutletControl(_BaseControl):
    """Outlet Control Class
    
    """

    def __init__(self, frame, name, column, sensors):
        """Initialize Class

        Inputs:
          frame:
          name:
          column:
        """
        _BaseControl.__init__(self)
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window

        # Relay commanded state -- Initialize as False = OFF
        self.RelayCmd = False
        self.sensors = sensors
        self._demand = False

        # Column Label for this outlet
        Label(frame, text=f"{name} (#{column+1})",
            bg='#f0f0f0').grid(row=OUTROW+1, column=column, sticky=W+E)

        # Individual Labels:
        self.onLabel = Label(frame, fg='green', bg='#e0ffe0',
                             text=f" ON {self.string_time(self.ONtime)}")
        self.offLabel = Label(frame, fg='red', bg='#ffe0e0',
                              text=f" OFF {self.string_time(self.OFFtime)}")
        self.tmpLabel = Label(frame, fg='blue', bg='#e0e0ff',
                      text=f" Coop Temp {self.string_temp(self.SWCHtmp)}")

        # Enable Box
        self.enableBox = Checkbutton(frame, text='Enable', variable=self.en_var, 
                                     command=self.update_enable, onvalue=True, 
                                     offvalue=False)

        # Sliders
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
                                     command=self.update_andor, bg='#e0e0e0',
                                     selectcolor='#50C878')
        self.orButton = Radiobutton(self.andorFrame, indicatoron=0, value=False,
                                    text='   OR   ', variable=self.bool_var,
                                    command=self.update_andor, bg='#e0e0e0',
                                    selectcolor='#50C878')

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

        self.cmdTxt = Label(frame, '', fg='black', bg='#f0f0f0', text='CMD: OFF')

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
        self.cmdTxt.grid(row=OUTROW+13, column=column, sticky=W+E)

    def update_temp_trigger(self,seltemp):
        self.SWCHtmp = int(seltemp)
        self.tmpLabel.config(text=f" Coop Temp {self.string_temp(self.SWCHtmp)}")

    def update_andor(self):
        self.ANDOR = self.bool_var.get()

    def update_temp_direction(self):
        self.TD = self.int_var.get()

    def cmd_state(self, nowobj, use_cache=False):
        # If 'ENABLE' box not checked, keep off
        if not self.ENABLE:
            return False

        # Get time commanded state
        nowh = nowobj.hour + nowobj.minute/60. + nowobj.second/3600.
        # ON-OFF-ON
        if self.TimeCycle == 1:
            timecmd = \
                False if nowh > self.OFFtime and nowh < self.ONtime else True
        # OFF-ON-OFF
        elif self.TimeCycle == 2:
            timecmd = \
                True if nowh > self.ONtime and nowh < self.OFFtime else False
        # Always ON
        else:
            timecmd = True
        
        # Get temperature commanded state
        intemp = self.sensors['inside'].temp if not use_cache else \
            self.sensors['inside'].cache_temp
        # ON above
        if self.TD == 1:
            tempcmd = True if intemp > self.SWCHtmp else False
        # ON below
        elif self.TD == -1:
            tempcmd = True if intemp < self.SWCHtmp else False
        # Temperature Independent
        else:
            tempcmd = None

        # Combine using AND/OR
        if tempcmd is None:
            return timecmd
        else:
            return timecmd and tempcmd if self.ANDOR else timecmd or tempcmd

    @property
    def demand(self):
        now = datetime.datetime.now()
        self._demand = self.cmd_state(now)
        return self._demand

    @property
    def state(self):
        now = datetime.datetime.now()
        return self.cmd_state(now, use_cache=True)


class DoorControl(_BaseControl):
    """Door Control Class
    
    """

    def __init__(self, frame):
        """Initialize Class

        Inputs:
          frame:
        """
        _BaseControl.__init__(self)
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window


        # Column 0: ENABLE
        self.doorEnable = Checkbutton(frame, text='Enable', onvalue=True,
                                      offvalue=False, variable=self.en_var,
                                      command=self.update_enable)
        
        # Column 1: Open Time
        self.onLabel = Label(frame, fg='green', bg='#e0ffe0',
                             text=f" OPEN {self.string_time(self.ONtime)}")
        self.doorOpenSlider = Scale(frame, from_=0, to=24, digits=4,
                                    orient=HORIZONTAL, resolution=0.25,
                                    command=self.update_on_time, showvalue=0,
                                    variable=DoubleVar, length=slider_size,
                                    troughcolor='#bfd9bf')
        
        # Column 2: Close Time
        self.offLabel = Label(frame, fg='red', bg='#ffe0e0',
                              text=f" CLOSE {self.string_time(self.OFFtime)}")
        self.doorCloseSlider = Scale(frame, from_=0, to=24, digits=4,
                                     orient=HORIZONTAL, resolution=0.25,
                                     command=self.update_off_time,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#d9bfbf')
        
        # Column 3: Light Trigger
        self.SWCHtmp = 2
        self.doorLightLabel = Label(frame, fg='#9932cc', bg='#f3e6f9',
                                    text=f" LIGHT {self.string_light(self.SWCHtmp)}")
        self.doorLightSlider = Scale(frame, from_=2, to=4, digits=4,
                                     orient=HORIZONTAL, resolution=0.05,
                                     command=self.update_door_light,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#cfc4d4')
        
        # Set everything to the grid
        self.doorEnable.grid(row=DOORROW+1, column=0, rowspan=2)
        self.onLabel.grid(row=DOORROW+1, column=1, sticky=W+E)
        self.doorOpenSlider.grid(row=DOORROW+2, column=1, sticky=W+E)
        self.offLabel.grid(row=DOORROW+1, column=2, sticky=W+E)
        self.doorCloseSlider.grid(row=DOORROW+2, column=2, sticky=W+E)
        self.doorLightLabel.grid(row=DOORROW+1, column=3, sticky=W+E)
        self.doorLightSlider.grid(row=DOORROW+2, column=3, sticky=W+E)
        
    # Light Update Method
    def update_door_light(self, seltime):
        self.SWCHtmp = float(seltime)
        self.doorLightLabel.config(text=f" LIGHT {self.string_light(self.SWCHtmp)}")



#=========================================================#
# Dummy Sensors for testing of the code NOT on a RPi
def setup_dummy_sensor():
    sensors = {}
    sensors['box'] = DummySensor()
    sensors['inside'] = DummySensor()
    sensors['outside'] = DummySensor()
    sensors['light'] = DummySensor()
    return sensors

class DummySensor:
    def __init__(self):
        self.temp = -99
        self.humid = -99
        self.lux = -99

class DummyRelay:
    _WRITE_BUF = bytearray(5)
    def __init__(self):
        self.state = [False] * 4
    def write(self):
        self._WRITE_BUF[0] = 0x01
        for i, r in enumerate(self.state, 1):
            self._WRITE_BUF[i] = 0xff if r else 0x00
