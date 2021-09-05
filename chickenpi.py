#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: chickenpi.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-in/Generic Imports
from tkinter import Tk      # Tk for display window
# […]

# Libs
# […]

# Own modules
#from {path} import {class}
from chicken_control import *

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2021, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.2.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 3 - Alpha'


### Main Routine ###
def main():
    root = Tk()
    app = ControlWindow(root)
    try:
        app.update()
        root.mainloop()
    finally:
        print("Exiting...")

if __name__ == '__main__':
    main()
