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

### Constants
WIDGET_WIDE  = 600           # Width of the "Status Window"
WIDGET_HIGH  = 300           # Height of the "Status Window"
STATBG       = 'black'
FONTSIZE     = 14
DATAFIELD    = 10

class StatusWindow():
    """
    StatusWindow class
    Creates the status window and (supposedly) updates it from time to time.
    """
    def __init__(self, master, CONTROL_WIDTH):
        """
        __init__ method: initializes the Status Window
        """
        # Define the MASTER for the window, set geometry
        self.master = master
        self.master.geometry(
            f"{WIDGET_WIDE}x{WIDGET_HIGH}+{CONTROL_WIDTH+10}+{PI_TOOLBAR}")
        self.master.title("Status Window")
        self.master.configure(bg=STATBG)

        # A "frame" holds the various window contents
        self.frame = Frame(self.master, bg=STATBG)
        self.frame.pack(expand=0)

        self.count = 0

        # Put the time at the top of the window
        self.dispTime = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                              bg=STATBG, fg='lightblue')
        self.dispTime.grid(row=0, columnspan=4)
        
        # Create the various section labels
        self.envLabel = self.make_sect_label('Environmental Status', row=1)
        self.netLabel = self.make_sect_label('Network Status', row=5)
        self.devLabel = self.make_sect_label('Device Status', row=8)

        # Environmental Status Labels
        self.envOutsLab = self.make_stat_label('    Outside:', row=2, column=0)
        self.envNestLab = self.make_stat_label('      Nests:', row=3, column=0)
        self.envRoosLab = self.make_stat_label('     Roosts:', row=4, column=0)
        self.envLighLab = self.make_stat_label('      Light:', row=2, column=2)
        self.envCPUTLab = self.make_stat_label('        CPU:', row=3, column=2)

        # Environmental Status Data
        self.envOutsDat = self.make_stat_data(row=2, column=1)
        self.envNestDat = self.make_stat_data(row=3, column=1)
        self.envRoosDat = self.make_stat_data(row=4, column=1)
        self.envLighDat = self.make_stat_data(row=2, column=3)
        self.envCPUTDat = self.make_stat_data(row=3, column=3)

        # Network Status Labels
        self.netWiFiLab = self.make_stat_label('WiFi Status:', row=6, column=0)
        self.netInetLab = self.make_stat_label('WLAN Status:', row=7, column=0)
        self.netLANaLab = self.make_stat_label('   Local IP:', row=6, column=2)
        self.netWANaLab = self.make_stat_label('    WLAN IP:', row=7, column=2)
        
        # Network Status Data
        self.netWiFiDat = self.make_stat_data(row=6, column=1)
        self.netInetDat = self.make_stat_data(row=7, column=1)
        self.netLANaDat = self.make_stat_data(row=6, column=3)
        self.netWANaDat = self.make_stat_data(row=7, column=3)

        # Device Status Labels
        self.devOut1Lab = self.make_stat_label('   Outlet 1:', row=9, column=0)
        self.devOut2Lab = self.make_stat_label('   Outlet 2:', row=9, column=2)
        self.devOut3Lab = self.make_stat_label('   Outlet 3:', row=10, column=0)
        self.devOut4Lab = self.make_stat_label('   Outlet 4:', row=10, column=2)
        self.devDoorLab = self.make_stat_label('       Door:', row=11, column=0)

        # Device Status Data
        self.devOut1Dat = self.make_stat_data(row=9, column=1)
        self.devOut2Dat = self.make_stat_data(row=9, column=3)
        self.devOut3Dat = self.make_stat_data(row=10, column=1)
        self.devOut4Dat = self.make_stat_data(row=10, column=3)
        self.devDoorDat = self.make_stat_data(row=11, column=1)



    # Label Creator Methods
    def make_sect_label(self, text, row):
        label = Label(self.frame, font=('times', FONTSIZE, 'bold'),
                      bg=STATBG, fg='yellow', text=text)
        label.grid(row=row, columnspan=4)
        return label

    def make_stat_label(self, text, row, column):
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='lightgreen', text=text)
        label.grid(row=row, column=column)
        return label

    def make_stat_data(self, row, column):
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='green', width=DATAFIELD)
        label.grid(row=row, column=column)
        return label


    def close_window(self):
        self.master.destroy()
        
        
    def update(self):
        now = datetime.datetime.now()
        self.dispTime.config(text=now.strftime("%d-%b-%y %H:%M:%S"))
        #self.frame.after(5000, self.update)
        self.count += 1
        # self.envstat1.config(text='{:d}\n{:d}\n{:d}'.format(
        #     self.count,self.count+1,self.count+2))
        # self.envstat2.config(text='{:d}\n{:d}'.format(
        #     self.count+3,self.count+4))
