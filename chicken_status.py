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
# […]

# Libs
import numpy as np         # Numpy!
import urllib3
import socket
from requests import get

# Own modules
#from {path} import {class}
try:
    from chicken_relay import *
    relay = Relay()   # Instantiate class
except:
    pass

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2021, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.2.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 3 - Alpha'

PI_TOOLBAR = 36
TK_HEADER  = 25

### Constants
WIDGET_WIDE  = 600           # Width of the "Status Window"
WIDGET_HIGH  = 300           # Height of the "Status Window"
STATBG       = 'black'
FONTSIZE     = 13
DATAFIELD    = 15
ENVROW       = 1
DEVROW       = 5
NETROW       = 9

# Enable testing on both Raspberry Pi and Mac
if os.path.exists("/usr/bin/uname"):
    _UNAME = "/usr/bin/uname"
elif os.path.exists("/bin/uname"):
    _UNAME = "/bin/uname"
else:
    _UNAME = ""
SYSTYPE = (os.popen(f"{_UNAME} -a").read()).split()[0]
WLAN = 'en0' if SYSTYPE == 'Darwin' else 'wlan0'




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

        # Put the time at the top of the window
        self.dispTime = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                              bg=STATBG, fg='skyblue')
        self.dispTime.grid(row=0, columnspan=4)
        
        # Create the various section labels
        self.make_sect_label('Environmental Status', row=ENVROW)
        self.make_sect_label('Network Status', row=NETROW)
        self.make_sect_label('Device Status', row=DEVROW)

        # Environmental Status Labels
        self.make_stat_label('    Outside:', row=ENVROW+1, column=0)
        self.make_stat_label('Inside Coop:', row=ENVROW+2, column=0)
        self.make_stat_label('Light Level:', row=ENVROW+3, column=0)
        self.make_stat_label(' Inside Box:', row=ENVROW+1, column=2)
        self.make_stat_label('   RPi4 CPU:', row=ENVROW+2, column=2)

        # Environmental Status Data
        self.envOutsDat = self.make_stat_data(row=ENVROW+1, column=1)
        self.envInsiDat = self.make_stat_data(row=ENVROW+2, column=1)
        self.envLighDat = self.make_stat_data(row=ENVROW+3, column=1)
        self.envChPiDat = self.make_stat_data(row=ENVROW+1, column=3)
        self.envCPUTDat = self.make_stat_data(row=ENVROW+2, column=3)

        # Network Status Labels
        self.make_stat_label('WiFi Status:', row=NETROW+1, column=0)
        self.make_stat_label('WLAN Status:', row=NETROW+2, column=0)
        self.make_stat_label('   Local IP:', row=NETROW+1, column=2)
        self.make_stat_label('    WLAN IP:', row=NETROW+2, column=2)
        
        # Network Status Data
        self.netWiFiDat = self.make_stat_data(row=NETROW+1, column=1)
        self.netInetDat = self.make_stat_data(row=NETROW+2, column=1)
        self.netLANaDat = self.make_stat_data(row=NETROW+1, column=3)
        self.netWANaDat = self.make_stat_data(row=NETROW+2, column=3)

        # Device Status Labels
        self.make_stat_label('   Outlet 1:', row=DEVROW+1, column=0)
        self.make_stat_label('   Outlet 2:', row=DEVROW+2, column=0)
        self.make_stat_label('   Outlet 3:', row=DEVROW+1, column=2)
        self.make_stat_label('   Outlet 4:', row=DEVROW+2, column=2)
        self.make_stat_label('       Door:', row=DEVROW+3, column=0)

        # Device Status Data
        self.devOutDat = []
        self.devOutDat.append(self.make_stat_data(row=DEVROW+1, column=1))
        self.devOutDat.append(self.make_stat_data(row=DEVROW+2, column=1))
        self.devOutDat.append(self.make_stat_data(row=DEVROW+1, column=3))
        self.devOutDat.append(self.make_stat_data(row=DEVROW+2, column=3))
        self.devDoorDat = self.make_stat_data(row=DEVROW+3, column=1)


    # Label Creator Methods
    def make_sect_label(self, text, row):
        label = Label(self.frame, font=('times', FONTSIZE, 'bold'),
                      bg=STATBG, fg='thistle2', text=text)
        label.grid(row=row, columnspan=4)
        return label

    def make_stat_label(self, text, row, column):
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='lightgreen', text=text)
        label.grid(row=row, column=column)
        return label

    def make_stat_data(self, row, column):
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='burlywood1', width=DATAFIELD)
        label.grid(row=row, column=column)
        return label

    def format_th_str(self, temp, humid):
        return f"{temp:.1f}\xb0F, {humid:.1f}%"

    def format_cpu_str(self, cputemp):
        return f"{cputemp:0.0f}\xb0F (<185\xb0F)" if cputemp is not None \
            else "----- (<185\xb0F)"

    def close_window(self):
        self.master.destroy()


    def update(self, now, sensors, relays):

        # Get the current time, and write
        self.dispTime.config(text = 
            now.strftime("%A, %B %-d, %Y    %-I:%M:%S %p"))

        # Set data update intervals
        short_interval = True if now.second % 15 == 0 else False
        long_interval = True if now.second % 60 == 0 else False

        # Write the various environment statuses at different intervals
        if short_interval:
            self.envCPUTDat.config(text = self.format_cpu_str(get_cpu_temp()))
        if long_interval:
            self.envInsiDat.config(text = 
                self.format_th_str(sensors['inside'].temp, sensors['inside'].humid))
            self.envOutsDat.config(text =
                self.format_th_str(sensors['outside'].temp, sensors['outside'].humid))
            self.envChPiDat.config(text =
                self.format_th_str(sensors['box'].temp, sensors['box'].humid))

        # Write the various device statuses at different intervals
        if short_interval:
            for i, dev in enumerate(self.devOutDat):
                dev.config(text = 'ENERGIZED' if relays.state[i] else 'OFF')

        # Write the various network statuses
        if short_interval:
            self.netLANaDat.config(text = get_local_IP())
            self.netWiFiDat.config(text =
                'ON' if contact_server('192.168.0.1') else 'OFF')
        if long_interval:
            self.netInetDat.config(text =
                'ON' if contact_server('1.1.1.1') else 'OFF')
            self.netWANaDat.config(text = get_public_IP())

        # For short update interval, wait an additional 0.5 s before returning
        if short_interval:
            time.sleep(0.5)



# Network Checking Functions
def contact_server(host='192.168.0.1'):
    """contact_server Check whether a server is reachable

    [extended_summary]

    Parameters
    ----------
    host : `str`, optional
        Name or IP address of server to contact [Default: '192.168.0.1']

    Returns
    -------
    `bool`
        Whether server is reachable
    """
    try:
        http = urllib3.PoolManager()
        http.request('GET', host, timeout=3, retries=False)
        return True
    except:
        return False


def get_local_IP():
    """get_local_IP Return the local (LAN) IP address for the Pi

    Use `ifconfig` to read the local IP address assigned to the Pi by the
    local DHCP server.

    Returns
    -------
    `str`
        LAN IP address
    """
    cmd = f"/sbin/ifconfig {WLAN} | grep 'inet ' | awk '{{print $2}}'"
    return (os.popen(cmd).read()).strip()


def get_public_IP():
    """get_public_IP Return the public-facing IP address for the Pi

    Query ipify.org to return the public (WAN) IP address for the network
    appliance to which the Chicken-Pi is attached.

    If an error message is kicked by ipify.org, then the response will be
    longer than the maximum 15 characters (xxx.xxx.xxx.xxx).  In this case,
    the function will return '-----' rather than an IP address.

    Returns
    -------
    `str`
        Public IP address
    """
    try:
        publicIP = (get('https://api.ipify.org').text).strip()
        # If response is longer than the maximum 15 characters, return '---'.
        if len(publicIP) > 15:
            publicIP = '-----'
    except:
        publicIP = '-----'
    return publicIP


# Environmental Checking Functions
def get_cpu_temp():
    """get_cpu_temp Read the CPU temperature from system file

    [extended_summary]

    Returns
    -------
    `float`
        CPU temperature in ºF
    """
    # Check Pi CPU Temp:
    if SYSTYPE == 'Linux':
        cputemp_fn = "/sys/class/thermal/thermal_zone0/temp"
        with open(cputemp_fn,"r") as f:
            return (float(f.read()) /1000.) * 9./5. + 32.
    return None


# Status Checking Functions
def get_outlet_status():
    try:
        # Read the relay_status
        return relay.status()
    except:
        return [False] * 4
