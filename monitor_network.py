#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: monitor network.py

Monotors and displays the current network status -- fixes as necessary

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
import urllib3
import socket
from requests import get
# […]

# Own modules
#from {path} import {class}
import private_emailer as em

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 1 - Planning'



# (1) Define the DISPLAY STRING & open file for write
root = Tk()
val1 = ''
ipaddr = ''
disp = Label(root, font=('courier', 14, 'bold'), bg='lightblue', fg='darkgreen')
disp.pack(fill=BOTH, expand=1)
abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
IPFN = abspath+'/.ipaddr.txt'

if os.path.isfile(IPFN):
  with open(IPFN, "r") as ipfile:
    ipaddr = ipfile.read()
    ipaddr.rstrip('\n')
    
### Functions for looking for wifi/internet connectivity
def wifi_on(host='192.168.0.1'):
  try:
    http = urllib3.PoolManager()
    http.request('GET', host, timeout=3, retries=False)
    return True
  except urllib3.exceptions.ConnectionError:
    return False
  

def internet_on(host='8.8.8.8', port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    return False


# (2) Method for updating DISPLAY STRING
def update():
  global val1         # Make available globally
  global ipaddr       # Make available globally
  
  # Check network connectivity
  wifi = 'ON' if wifi_on() else 'OFF'
  internet = 'ON' if internet_on() else 'OFF'
  hostname = socket.gethostname()
  localIP = (os.popen(
    "/sbin/ifconfig wlan0 | grep 'inet ' | awk '{print $2}'").
             read()).rstrip()
  publicIP = get('https://api.ipify.org').text
  publicIP.rstrip()
  # If error message kicked by ipify.org, then publicIP will be longer than the
  #  maximum 15 characters (xxx.xxx.xxx.xxx).  Set to empty string.
  if len(publicIP) > 15:
    publicIP = ''
    
  # Get the current time
  now = datetime.datetime.now()
  val2 = "{:s}\n\nWiFi Status: {:s}\nInternet Status: {:s}\nLocal IP: {:s}\nPublic IP: {:s}".format(now.strftime("%d-%b-%y %H:%M:%S"),
                                                                                                    wifi, internet, localIP, publicIP)
  
  # Update the DISPLAY STRING
  if val2 != val1:
    val1 = val2
    disp.config(text=val2)
    
  # Send email with current IP address
  if publicIP == "":
    pass                      # Don't do anything...
  elif publicIP != ipaddr:
    ipaddr = publicIP         # Update the IP address
    sender = em.Emailer()
    sendTo = 'chickenpi.flag@gmail.com'
    emailSubject = 'Chicken-Pi IP Address'
    emailContent = 'Current chicken-pi IP address: '+publicIP
    sender.sendmail(sendTo, emailSubject, emailContent)
    with open(IPFN, "w") as ipfile:
      ipfile.write(publicIP)
  
  # This Method calls itself every minute to update the display
  disp.after(60000, update)



# (3) Call the loop for Tk to DISPLAY STRING
update()
root.winfo_toplevel().title("Network Status")
root.geometry("+0+300")
root.mainloop()
