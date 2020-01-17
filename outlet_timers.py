# outlet_timers.py
from tkinter import *      
import time
import datetime
import board
import busio
import numpy as np
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

import chicken_relay as relay

_ADDR        = const(0x10)  # Address of the relay board
_COMMAND_BIT = const(0x01)  # Apparent command bit of relay board
OUT1STR      = "Heat Lamp"
OUT2STR      = "Red Light"
OUT3STR      = "_________"
OUT4STR      = "_________"
WIDGET_WIDE  = 600
WIDGET_HIGH  = 250

# group together all of the GUI code into a class called App
class App:

    # This function gets called upon creation
    def __init__(self, master):

        # Initialize the various variables required
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
        
        
        # A frame holds the various GUI controls
        self.frame = Frame(master)
        self.frame.pack(expand=1)#fill=BOTH, expand=1)

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
        Checkbutton(self.frame, text='Enable', onvalue=True, offvalue=False,
                    variable=self.var1,
                    command=self.update1ENABLE).grid(row=1, column=0)
        Checkbutton(self.frame, text='Enable', onvalue=True, offvalue=False,
                    variable=self.var2,
                    command=self.update2ENABLE).grid(row=1, column=1)
        Checkbutton(self.frame, text='Enable', onvalue=True, offvalue=False,
                    variable=self.var3,
                    command=self.update3ENABLE).grid(row=1, column=2)
        Checkbutton(self.frame, text='Enable', onvalue=True, offvalue=False,
                    variable=self.var4,
                    command=self.update4ENABLE).grid(row=1, column=3)
        
        ## Create the sliders and position them in a grid layout
        ## the 'command' attribute specifies a method to call when
        ## a slider is moved
        # Outlet #1
        slider_size = (WIDGET_WIDE - 5*10) / 4
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update1ON, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=3,column=0)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update1OFF, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=5,column=0)
        # Outlet #2
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update2ON, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=3,column=1)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update2OFF, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=5,column=1)
        # Outlet #3
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update3ON, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=3,column=2)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update3OFF, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=5,column=2)
        # Outlet #4
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update4ON, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=3,column=3)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update4OFF, resolution=0.25, digits=4,
              variable=DoubleVar, length=slider_size).grid(row=5,column=3)
        
        
    # These methods called whenever a checkbox is clicked
    def update1ENABLE(self):
        self.ENABLE1 = self.var1.get()

    def update2ENABLE(self):
        self.ENABLE2 = self.var2.get()

    def update3ENABLE(self):
        self.ENABLE3 = self.var3.get()

    def update4ENABLE(self):
        self.ENABLE4 = self.var4.get()
        
    # These methods called whenever a slider moves
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

        
    # Make the string for display of the time
    def makeStringTime(self,inTime):
        # Compute minutes from decimal hour
        minute = 60 * (inTime % 1)
        # Catch case of 24:00:00
        if inTime == 24:
            inTime = 0
        # Set PM/AM times
        if inTime >= 12:
            ampm = "PM"
            inTime -= 12
        else:
            ampm = "AM"
        # Catch case of 0:00:00
        if int(inTime) == 0:
            inTime = 12

        return "{:2d}:{:0>2d} {:s}".format(int(inTime),int(minute),ampm)


    # Function to return ON/OFF based on relay state
    def onoffstr(self,statevar):
        return "ON  " if statevar != 0x00 else "OFF "
    
    
    # Function to return the ON/OFF cycle for the relay
    def onoff_cycle(self, ontime, offtime):
        if abs(ontime - offtime) == 24:  # equal: ON always, special case
            cycle = 3
        elif ontime > offtime:           # ON - OFF - ON
            cycle = 1
        elif ontime < offtime:           # OFF - ON - OFF
            cycle = 2
        else:                            # equal: ON always
            cycle = 4
        return cycle
    
    
    # Function to determine relay state based on time, cycle
    def relay_state(self, cycle, ontime, offtime):
        nowh = self.nowhour
        if cycle == 1:
            restate = False if nowh > offtime and nowh < ontime else True
        elif cycle == 2:
            restate = True if nowh > ontime and nowh < offtime else False
        else:
            restate = True
        return restate
    
    
    # Function to update every 5 seconds
    def update(self):

        # Get the time at the start of the method call, particularly HH.HHHH
        now = datetime.datetime.now()
        self.nowhour = now.hour + now.minute/60 + now.second/3600
        
        # Adjust the relays, as needed based on the time.
        cycle1 = self.onoff_cycle(self.ON1time, self.OFF1time)
        cycle2 = self.onoff_cycle(self.ON2time, self.OFF2time)
        cycle3 = self.onoff_cycle(self.ON3time, self.OFF3time)
        cycle4 = self.onoff_cycle(self.ON4time, self.OFF4time)
        
        # Figure out when it is, with relation to cycle
        relay1state = self.relay_state(cycle1, self.ON1time, self.OFF1time)
        relay2state = self.relay_state(cycle2, self.ON2time, self.OFF2time)
        relay3state = self.relay_state(cycle3, self.ON3time, self.OFF3time)
        relay4state = self.relay_state(cycle4, self.ON4time, self.OFF4time)

        # Conflate time-based state with ENABLE checkbox to construct
        # output bytearray to write to Relay Board via I2C
        set1state = relay1state and self.ENABLE1
        set2state = relay2state and self.ENABLE2
        set3state = relay3state and self.ENABLE3
        set4state = relay4state and self.ENABLE4

        # Write the states!
        relay.write_relay(set1state, set2state, set3state, set4state)
                
        # Determine current states of the relays
        state = relay.read_relay()
        
        R1str = "  "+OUT1STR+" is " + self.onoffstr(state[1])
        R2str = "  "+OUT2STR+" is " + self.onoffstr(state[2])
        R3str = "  "+OUT3STR+" is " + self.onoffstr(state[3])
        R4str = "  "+OUT4STR+" is " + self.onoffstr(state[4])
        
        relayval = "{:s}\n{:s}\n{:s}\n{:s}".format(R1str,R2str,R3str,R4str)
        disprelay = Label(self.frame, font=('courier', 14, 'bold'),
                          fg='darkgreen')
        disprelay.grid(row=7, column=2, columnspan=2)
        disprelay.config(text=relayval)
                
        ### Create output strings for display
        # Time
        disptime = Label(self.frame, font=('courier', 14, 'bold'), fg='darkblue')
        disptime.grid(row=6, column=0, columnspan=4)
        disptime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))

        val2="{:b} {:b} {:b} {:b}\n{:d} {:d} {:d} {:d}\n{:b} {:b} {:b} {:b}\n{:b} {:b} {:b} {:b}".format(self.ENABLE1,self.ENABLE2,self.ENABLE3,self.ENABLE4,
                                                                                                         cycle1,cycle2, cycle3, cycle4,
                                                                                                         relay1state, relay2state, relay3state, relay4state,
                                                                                                         set1state, set2state, set3state, set4state)
        disp = Label(self.frame, font=('courier', 14, 'bold'), fg='darkred')
        disp.grid(row=7, column=0, columnspan=2)
        disp.config(text=val2)
        disp.after(5000, self.update)



        
# Set the GUI running, give the window a title, size, and position
root = Tk()
root.wm_title('Outlet Timers')
app = App(root)
root.geometry("{:d}x{:d}+0+0".format(WIDGET_WIDE,WIDGET_HIGH))
try:
    app.update()
    root.mainloop()
finally:
    print("Ending")
