#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: outlet_timers.py

Controls the 4 outlets on the chicken-pi based on time and ENABLE

"""
""

# Futures
# […]

# Built-in/Generic Imports
from tkinter import *      # Tk for display window      
import datetime            # Date & Time
import os,sys              # Search for file on disk
import csv                 # For CSV output
import atexit              # Register cleanup functions
# […]

# Libs
# […]

# Own modules
#from {path} import {class}
import chicken_relay as relay


## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi@gmail.com'
__status__ = 'Development Status :: 1 - Planning'


### Constants
OUT1STR      = "Heat Lamp"  # Name of what is plugged into outlet #1
OUT2STR      = "Red Light"  # Name of what is plugged into outlet #2
OUT3STR      = "Heat Lamp"  # Name of what is plugged into outlet #3
OUT4STR      = "_________"  # Name of what is plugged into outlet #4
WIDGET_WIDE  = 600          # Width of the "Outlet Timers" window
WIDGET_HIGH  = 250          # Height of the "Outlet Timers" window


### Define location of the state file containing current slider / checkbox vals
STATEFN = os.path.abspath(os.path.dirname(sys.argv[0]))+'/.outlet_state.txt'


### Group together all of the GUI code into a class called App
class App:
    """
    class App: contains all of the GUI code needed for the Outlet Timers
               window.  Contains the following methods:
    __init__ : Initializes the main functions of the window, including the
               column labels, ENABLE checkboxes, and slider bars.
    
    """

    ### This function gets called upon creation
    def __init__(self, master):

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

        ## A "frame" holds the various GUI controls
        self.frame = Frame(master)
        self.frame.pack(expand=0)

        ## Create the labels and position them in a grid layout
        # Outlet #1
        Label(self.frame, text=OUT1STR+' (#1)').grid(row=0,column=0)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON1time),
              fg='green').grid(row=2,column=0)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF1time)
              , fg='red').grid(row=4,column=0)
        # Outlet #2
        Label(self.frame, text=OUT2STR+' (#2)').grid(row=0,column=1)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON2time),
              fg='green').grid(row=2,column=1)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF2time),
              fg='red').grid(row=4,column=1)
        # Outlet #3
        Label(self.frame, text=OUT3STR+' (#3)').grid(row=0,column=2)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON3time),
              fg='green').grid(row=2,column=2)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF3time),
              fg='red').grid(row=4,column=2)
        # Outlet #4
        Label(self.frame, text=OUT4STR+' (#4)').grid(row=0,column=3)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON4time),
              fg='green').grid(row=2,column=3)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF4time),
              fg='red').grid(row=4,column=3)
        
        ## Create an 'ENABLE' checkbox for each outlet
        self.EN1 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var1,
                               command=self.update1ENABLE)
        self.EN1.grid(row=1, column=0)
        self.EN2 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var2,
                               command=self.update2ENABLE)
        self.EN2.grid(row=1, column=1)
        self.EN3 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var3,
                               command=self.update3ENABLE)
        self.EN3.grid(row=1, column=2)
        self.EN4 = Checkbutton(self.frame, text='Enable', onvalue=True,
                               offvalue=False, variable=self.var4,
                               command=self.update4ENABLE)
        self.EN4.grid(row=1, column=3)
        
        ## Create the sliders and position them in a grid layout.
        ## The 'command' attribute specifies a method to call when
        ## a slider is moved
        # Outlet #1
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window
        self.S1ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update1ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S1ON.grid(row=3,column=0)
        self.S1OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update1OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S1OFF.grid(row=5,column=0)
        # Outlet #2
        self.S2ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update2ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S2ON.grid(row=3,column=1)
        self.S2OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update2OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S2OFF.grid(row=5,column=1)
        # Outlet #3
        self.S3ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update3ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S3ON.grid(row=3,column=2)
        self.S3OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update3OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S3OFF.grid(row=5,column=2)
        # Outlet #4
        self.S4ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          showvalue=0,command=self.update4ON,resolution=0.25,
                          digits=4, variable=DoubleVar, length=slider_size)
        self.S4ON.grid(row=3,column=3)
        self.S4OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                           showvalue=0,command=self.update4OFF,resolution=0.25,
                           digits=4, variable=DoubleVar, length=slider_size)
        self.S4OFF.grid(row=5,column=3)

        ## If extant, read in the state file and restore sliders and checkboxes
        ##  to last known values
        if os.path.isfile(STATEFN):
            with open(STATEFN, 'r') as statefile:
                stateReader = csv.reader(statefile, delimiter=',')
                for states in stateReader:
                    self.readPrevStates(states)


    ### This method reads in saved states and makes the appropriate changes
    def readPrevStates(self,states):

        # The ENABLE state variables
        for jj,box in zip(range(4),[self.EN1,self.EN2,self.EN3,self.EN4]):
            if int(states[jj]) == 0:
                box.deselect()
            else:
                box.select()
        self.update1ENABLE()
        self.update2ENABLE()
        self.update3ENABLE()
        self.update4ENABLE()

        # The TIME state variables
        self.S1ON.set(states[4])
        self.update1ON(states[4])
        self.S2ON.set(states[6])
        self.update2ON(states[6])
        self.S3ON.set(states[8])
        self.update3ON(states[8])
        self.S4ON.set(states[10])
        self.update4ON(states[10])
        self.S1OFF.set(states[5])
        self.update1OFF(states[5])
        self.S2OFF.set(states[7])
        self.update2OFF(states[7])
        self.S3OFF.set(states[9])
        self.update3OFF(states[9])
        self.S4OFF.set(states[11])
        self.update4OFF(states[11])
    
    
    ### The following methods are called whenever a checkbox is clicked:
    def update1ENABLE(self):
        self.ENABLE1 = self.var1.get()

    def update2ENABLE(self):
        self.ENABLE2 = self.var2.get()

    def update3ENABLE(self):
        self.ENABLE3 = self.var3.get()

    def update4ENABLE(self):
        self.ENABLE4 = self.var4.get()
    
    
    ### The following methods are called whenever a slider is moved:
    def update1ON(self,seltime):
        self.ON1time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON1time),
              fg='green').grid(row=2,column=0)
        
    def update1OFF(self,seltime):
        self.OFF1time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF1time),
              fg='red').grid(row=4,column=0)
        
    def update2ON(self,seltime):
        self.ON2time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON2time),
              fg='green').grid(row=2,column=1)
        
    def update2OFF(self,seltime):
        self.OFF2time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF2time),
              fg='red').grid(row=4,column=1)

    def update3ON(self,seltime):
        self.ON3time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON3time),
              fg='green').grid(row=2,column=2)
        
    def update3OFF(self,seltime):
        self.OFF3time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF3time),
              fg='red').grid(row=4,column=2)
        
    def update4ON(self,seltime):
        self.ON4time = float(seltime)
        Label(self.frame, text=' ON '+self.makeStringTime(self.ON4time),
              fg='green').grid(row=2,column=3)
        
    def update4OFF(self,seltime):
        self.OFF4time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF4time),
              fg='red').grid(row=4,column=3)

        
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


    ### This method returns a string "ON"/"OFF" based on relay state
    def onOffStr(self,statevar):
        return "ON  " if statevar != 0x00 else "OFF "
    
    
    ### This method defines a "cycle" of On/Off for the relay, used for
    ###  computing whether the relay should be on or off based on time of day
    def onOffCycle(self, ontime, offtime):
        if abs(ontime - offtime) == 24:  # equal: ON always, special case
            cycle = 3
        elif ontime > offtime:           # ON - OFF - ON
            cycle = 1
        elif ontime < offtime:           # OFF - ON - OFF
            cycle = 2
        else:                            # equal: ON always
            cycle = 4
        return cycle
    
    
    ### This method determines the commanded relay state based on time of day
    def relayState(self, ontime, offtime):
        nowh = self.nowhour
        # Determine the 'cycle' based on On/Off times
        cycle = self.onOffCycle(ontime, offtime)
        # Set commanded relay state based on current time
        if cycle == 1:
            restate = False if nowh > offtime and nowh < ontime else True
        elif cycle == 2:
            restate = True if nowh > ontime and nowh < offtime else False
        else:
            restate = True   # cycle = 3 or 4: both are ON always
        return restate
    
    
    ### This method self-calls every 5 seconds to update the display strings
    ###  and check/set the states of the relays
    def update(self):

        ## Get the time at the start of the method call, particularly HH.HHHH
        now = datetime.datetime.now()
        self.nowhour = now.hour + now.minute/60 + now.second/3600
        
        ## Adjust the relays, as needed based on the time.
        # Determine commanded relay state, based on current time
        relay1state = self.relayState(self.ON1time, self.OFF1time)
        relay2state = self.relayState(self.ON2time, self.OFF2time)
        relay3state = self.relayState(self.ON3time, self.OFF3time)
        relay4state = self.relayState(self.ON4time, self.OFF4time)

        # Conflate time-based state with ENABLE checkbox to construct
        #  output bytearray to write to Relay Board via I2C
        set1state = relay1state and self.ENABLE1
        set2state = relay2state and self.ENABLE2
        set3state = relay3state and self.ENABLE3
        set4state = relay4state and self.ENABLE4

        # Write the states!
        relay.write_relay(set1state, set2state, set3state, set4state)
                
        ## Determine current states of the relays for display on right side
        ##  of the widget window
        state = relay.read_relay()
        
        R1str = "  "+OUT1STR+" is " + self.onOffStr(state[1])
        R2str = "  "+OUT2STR+" is " + self.onOffStr(state[2])
        R3str = "  "+OUT3STR+" is " + self.onOffStr(state[3])
        R4str = "  "+OUT4STR+" is " + self.onOffStr(state[4])
        
        relayval = "{:s}\n{:s}\n{:s}\n{:s}".format(R1str,R2str,R3str,R4str)
        disprelay = Label(self.frame, font=('courier', 14, 'bold'),
                          fg='darkgreen')
        disprelay.grid(row=7, column=2, columnspan=2)
        disprelay.config(text=relayval)
        
        ## Create additional output strings for display
        # Time
        disptime = Label(self.frame, font=('courier', 14, 'bold'),
                         fg='darkblue')
        disptime.grid(row=6, column=0, columnspan=4)
        disptime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))

        # Debug values
        val2= "   Enable: {:b} {:b} {:b} {:b}\n".format(self.ENABLE1,self.ENABLE2,self.ENABLE3,self.ENABLE4)
        val2+="Commanded: {:b} {:b} {:b} {:b}\n".format(relay1state, relay2state, relay3state, relay4state)
        val2+="      Set: {:b} {:b} {:b} {:b}".format(set1state, set2state, set3state, set4state)
        disp = Label(self.frame, font=('courier', 14, 'bold'), fg='darkred')
        disp.grid(row=7, column=0, columnspan=2)
        disp.config(text=val2)

        # As the last display element described in self.update(), call this
        #  method again in 5 seconds to update the display.
        disp.after(5000, self.update)



        
### Main Program: Set the GUI running, give the window a title, size,
###  and position
root = Tk()
root.wm_title('Outlet Timers')
app = App(root)
root.geometry("{:d}x{:d}+0+0".format(WIDGET_WIDE,WIDGET_HIGH))
try:
    app.update()
    root.mainloop()
finally:
    print("Ending")
