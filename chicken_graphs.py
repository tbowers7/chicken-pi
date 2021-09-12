# -*- coding: utf-8 -*-

"""
  FILE: chicken_graphs.py

Graphs display window, updates occasionally with current values

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
import threading           # Threading to allow for NWS request
# […]

# Libs
# […]
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from noaa_sdk import noaa
from matplotlib.dates import DateFormatter, DayLocator, HourLocator

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


class GraphsWindow():
    def __init__(self, master):
        self.master = master
        self.master.geometry("700x400+600+{:d}".format(200+PI_TOOLBAR+TK_HEADER))
        self.master.title("Graphs Window")
        self.frame = Frame(self.master)

        # Load the local coordinates from file
        ABSPATH = os.path.abspath(os.path.dirname(sys.argv[0]))
        try:
            with open(ABSPATH+'/.lonlat.txt','r') as fileobj:
                coords = []
                for line in fileobj:
                    coords.append(line.rstrip())
        except:
            print("You must create a file .lonlat.txt containing the coordinates to submit to NOAA")
            exit()
        self.lat = coords[1]
        self.lon = coords[0]

        # Create the NOAA object instance
        self.n             = noaa.NOAA()
        self.have_forecast = False

        # Plot date formats
        self.alldays   = DayLocator()
        self.quartdays = HourLocator(byhour=[0,6,12,18])
        self.dayFormat = DateFormatter('%a %-m/%d')
        
      
        
        
    def close_window(self):
        self.master.destroy()
        

    ### GET FORECAST METHOD ###
    def get_forecast(self):
        try:
            forecast = self.n.points_forecast(self.lat,self.lon,hourly=False)
        except:
            self.have_forecast = False
            return
            
        nperiods = len(forecast['properties']['periods'])
        highTemp = []
        highDate = []
        lowTemp = []
        lowDate = []
        
        for x in range(0,nperiods):
            
            # For <= 3.6 compatibility, remove colon in time zone
            startTime  = forecast['properties']['periods'][x]['startTime']
            startTZcol = startTime.rindex(':')
            endTime    = forecast['properties']['periods'][x]['endTime']
            endTZcol   = endTime.rindex(':')
            
            startBlock = datetime.datetime.strptime(
                startTime[:startTZcol]+startTime[startTZcol+1:],
                "%Y-%m-%dT%H:%M:%S%z")
            endBlock = datetime.datetime.strptime(
                endTime[:endTZcol]+endTime[endTZcol+1:],
                "%Y-%m-%dT%H:%M:%S%z")
            midpoint = (startBlock + (endBlock - startBlock)/2)
            
            if forecast['properties']['periods'][x]['isDaytime']:
                highTemp.append(
                    forecast['properties']['periods'][x]['temperature'])
                highDate.append(midpoint)
            else:
                lowTemp.append(
                    forecast['properties']['periods'][x]['temperature'])
                lowDate.append(midpoint)
                
        self.highTemp = highTemp
        self.highDate = highDate
        self.lowTemp  = lowTemp
        self.lowDate  = lowDate
        
        self.have_forecast = True
        #print(lowDate)

        
    ### UPDATE METHOD ###
    def update(self, now):
        x = threading.Thread(target=self.get_forecast, daemon=True)
        x.start()
        print(self.have_forecast)
        print("Got here 0?")
        
        if self.have_forecast:
            f = Figure(figsize=(5,5), dpi=100)
            a = f.add_subplot(111)
            # a.xaxis.set_major_locator(self.alldays)
            # a.xaxis.set_minor_locator(self.quartdays)
            a.xaxis.set_major_formatter(self.dayFormat)
            a.grid(which='major',axis='x',color='#505050',linestyle='-')
            # a.grid(which='minor',axis='x',color='pink',linestyle='-')
            a.plot(self.highDate, self.highTemp, 'ro')
            a.plot(self.lowDate,  self.lowTemp, 'bo')
            a.plot(self.highDate, self.highTemp, 'r-')
            a.plot(self.lowDate,  self.lowTemp, 'b-')
            
            print("Got here 1?")
            canvas = FigureCanvasTkAgg(f, self.master)
            print("Got here 1a?")
            canvas.draw()
            print("Got here 1b?")
            canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
            
            print("Got here 2?")
            toolbar = NavigationToolbar2Tk(canvas, self.master)
            toolbar.update()
            canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
        
        
