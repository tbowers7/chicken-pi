# outlet_timers.py
from tkinter import *      
import time
import datetime
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

_ADDR        = const(0x10)  # Address of the relay board
_COMMAND_BIT = const(0x01)  # Apparent command bit of relay board


# group together all of the GUI code into a class called App
class App:

    # This function gets called upon creation
    def __init__(self, master):
        
        self.ON1time = 0
        self.OFF1time = 0
        self.ON2time = 0
        self.OFF2time = 0
        
        
        # A frame holds the various GUI controls
        self.frame = Frame(master)
        self.frame.pack()

        # Create the labels and position them in a grid layout
        Label(self.frame, text='Heat Lamp (#1) ON').grid(row=0,column=0)
        Label(self.frame, text='Heat Lamp (#1) OFF').grid(row=1,column=0)
        Label(self.frame, text='Red Light (#2) ON').grid(row=0,column=2)
        Label(self.frame, text='Red Light (#2) OFF').grid(row=1,column=2)

        # Create the sliders and position them in a grid layout
        # the 'command' attribute specifies a method to call when
        # a slider is moved
        scale1ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                         command=self.update1ON, resolution=0.25,
                         digits=4, variable=DoubleVar)
        scale1ON.grid(row=0,column=1)
        scale1OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          command=self.update1OFF, resolution=0.25,
                          digits=4, variable=DoubleVar)
        scale1OFF.grid(row=1,column=1)
        scale2ON = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                         command=self.update2ON, resolution=0.25,
                         digits=4, variable=DoubleVar)
        scale2ON.grid(row=0,column=3)
        scale2OFF = Scale(self.frame, from_=0, to=24, orient=HORIZONTAL,
                          command=self.update2OFF, resolution=0.25,
                          digits=4, variable=DoubleVar)
        scale2OFF.grid(row=1,column=3)

    # These methods called whenever a slider moves
    def update1ON(self,seltime):
        self.ON1time = float(seltime)
        #print('Heat Lamp On: {:0.2f}'.format(self.ON1time))
        
    def update1OFF(self,seltime):
        self.OFF1time = float(seltime)
        #print('Heat Lamp Off: {:0.2f}'.format(self.OFF1time))
        
    def update2ON(self,seltime):
        self.ON2time = float(seltime)
        #print('Red Light On: {:0.2f}'.format(self.ON2time))
        
    def update2OFF(self,seltime):
        self.OFF2time = float(seltime)
        #print('Red Light Off: {:0.2f}'.format(self.OFF2time))

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

    # Function to update every 5 seconds
    def update(self):
        # Determine current states of the relays
        
        
        
        
        
        
        # Adjust the relays, as needed based on the time.

        ### Create output strings for display
        # Time
        now = datetime.datetime.now()
        disptime = Label(self.frame, font=('courier', 14, 'bold'), fg='darkblue')
        disptime.grid(row=3, column=0, columnspan=4)
        disptime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))
        
        # Timer ON / OFF values
        ON1str = self.makeStringTime(self.ON1time)
        #print("Heat Lamp ON: {:s}".format(ON1str))
        OFF1str = self.makeStringTime(self.OFF1time)
        #print("Heat Lamp OFF: {:s}".format(OFF1str))
        ON2str = self.makeStringTime(self.ON2time)
        #print("Red Light ON: {:s}".format(ON2str))
        OFF2str = self.makeStringTime(self.OFF2time)
        #print("Red Light OFF: {:s}".format(OFF2str))

        
  
        # Create display string for window
        val2 = "Heat ON: {:s}\nHeat OFF: {:s}\nRed ON: {:s}\nRed OFF: {:s}".format(
            ON1str,OFF1str,ON2str,OFF2str)
        disp = Label(self.frame, font=('courier', 14, 'bold'), fg='darkred')
        disp.grid(row=4, column=0, columnspan=2)
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
