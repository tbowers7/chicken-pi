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
# […]

# Libs
# […]
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

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
        
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        
        
        
        canvas = FigureCanvasTkAgg(f, self.master)
        canvas.draw()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
        
        
        
    def close_window(self):
        self.master.destroy()
        
        
