# outlet_timers.py
from tkinter import *      
import time
import datetime
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

import chicken_relay as relay

_ADDR        = const(0x10)  # Address of the relay board
_COMMAND_BIT = const(0x01)  # Apparent command bit of relay board
OUT1STR      = "Heat Lamp"
OUT2STR      = "Red Light"
OUT3STR      = "_________"
OUT4STR      = "_________"

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

        ## Create the sliders and position them in a grid layout
        ## the 'command' attribute specifies a method to call when
        ## a slider is moved
        # Outlet #1
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update1ON, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=3,column=0)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update1OFF, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=5,column=0)
        # Outlet #2
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update2ON, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=3,column=1)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update2OFF, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=5,column=1)
        # Outlet #3
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update3ON, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=3,column=2)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update3OFF, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=5,column=2)
        # Outlet #4
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update4ON, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=3,column=3)
        Scale(self.frame, from_=0, to=24, orient=HORIZONTAL, showvalue=0,
              command=self.update4OFF, resolution=0.25, digits=4,
              variable=DoubleVar).grid(row=5,column=3)

    
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
        Label(self.frame, text=' OFF '+self.makeStringTime(self.ON3time),
              fg='green').grid(row=2,column=2)
        
    def update3OFF(self,seltime):
        self.OFF3time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.OFF3time),
              fg='red').grid(row=4,column=2)
        
    def update4ON(self,seltime):
        self.ON4time = float(seltime)
        Label(self.frame, text=' OFF '+self.makeStringTime(self.ON4time),
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

        strTime = "{:2d}:{:0>2d} {:s}".format(int(inTime),int(minute),ampm)
        return strTime


    # Function to return ON/OFF based on relay state
    def onoffstr(self,statevar):
        if statevar != 0x00:
            statestr = "ON  "
        else:
            statestr = "OFF "
        return statestr

    # Function to update every 5 seconds
    def update(self):
        # Determine current states of the relays
        state = relay.read_relay()

        R1str = "  "+OUT1STR+" is " + self.onoffstr(state[1])
        R2str = "  "+OUT2STR+" is " + self.onoffstr(state[2])
        R3str = "  "+OUT3STR+" is " + self.onoffstr(state[3])
        R4str = "  "+OUT4STR+" is " + self.onoffstr(state[4])

            
        relayval = "{:s}\n{:s}\n{:s}\n{:s}".format(R1str,R2str,R3str,R4str)
        disprelay = Label(self.frame, font=('courier', 14, 'bold'), fg='darkgreen')
        disprelay.grid(row=7, column=2, columnspan=2)
        disprelay.config(text=relayval)
        #print("State:")
        #print(state)
        
        
        # Adjust the relays, as needed based on the time.
        
        
        
        
        
        
        
        ### Create output strings for display
        # Time
        now = datetime.datetime.now()
        disptime = Label(self.frame, font=('courier', 14, 'bold'), fg='darkblue')
        disptime.grid(row=6, column=0, columnspan=4)
        disptime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))
        
        val2=""
        disp = Label(self.frame, font=('courier', 14, 'bold'), fg='darkred')
        disp.grid(row=7, column=0, columnspan=2)
        #disp.pack(fill=BOTH, expand=1)
        disp.config(text=val2)
        disp.after(5000, self.update)
        
# Set the GUI running, give the window a title, size, and position
root = Tk()
root.wm_title('Outlet Timers')
app = App(root)
root.geometry("500x250+0+0")
try:
    app.update()
    root.mainloop()
finally:
    print("Ending")
