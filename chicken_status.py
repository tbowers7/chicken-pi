# -*- coding: utf-8 -*-

"""
  FILE: chicken_status.py

Status display window, updates frequently with current values

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


class Status_Window:
    def __init__(self, master):
        self.master = master
        self.master.geometry("600x200+600+{:d}".format(PI_TOOLBAR))
        self.master.title("Status Window")
        self.frame = Frame(self.master)
        self.quit = Button(self.frame, text = f"Quit this window.", command = self.close_window)
        self.quit.pack()
        self.frame.pack()
        
    def close_window(self):
        self.master.destroy()
        
        
