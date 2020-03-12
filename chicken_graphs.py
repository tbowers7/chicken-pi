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
from datetime import datetime
# […]

# Libs
# […]
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from noaa_sdk import noaa

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


class Graphs_Window(Tk):
    def __init__(self, master):
        self.master = master
        self.master.geometry("700x400+600+{:d}".format(200+PI_TOOLBAR+TK_HEADER))
        self.master.title("Graphs Window")
        self.frame = Frame(self.master)

        # Load the local coordinates from file
        ABSPATH = os.path.abspath(os.path.dirname(sys.argv[0]))
        with open(ABSPATH+'/.lonlat.txt','r') as fileobj:
            coords = []
            for line in fileobj:
                coords.append(line.rstrip())
                
        self.lat = coords[1]
        self.lon = coords[0]
        
        self.n = noaa.NOAA()
        
        self.get_forecast()
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot(self.highDate, self.highTemp)
        a.plot(self.lowDate,  self.lowTemp)
        
        
        
        canvas = FigureCanvasTkAgg(f, self.master)
        canvas.draw()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
        
        
        
    def close_window(self):
        self.master.destroy()
        
        
    def get_forecast(self):
        forecast = self.n.points_forecast(self.lat,self.lon,hourly=False)

        nperiods = len(forecast['properties']['periods'])
        highTemp = []
        highDate = []
        lowTemp = []
        lowDate = []
        
        for x in range(0,nperiods):
            
            startBlock = datetime.strptime(
                forecast['properties']['periods'][x]['startTime'],
                "%Y-%m-%dT%H:%M:%S%z")
            endBlock = datetime.strptime(
                forecast['properties']['periods'][x]['endTime'],
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
