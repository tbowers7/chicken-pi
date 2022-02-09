#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: chickenpi.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-In Libraries
import atexit
import os
from tkinter import Tk      # Tk for display window

# 3rd Party Libraries

# Internal Imports
from chicken.control import ControlWindow

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2021, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.5.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 3 - Alpha'


#===================================================================#
def main(args):
    """
    Main function
    """
    base_dir = os.path.abspath(os.path.dirname(args[0]))


    root = Tk()
    app = ControlWindow(root, base_dir)
    atexit.register(app.write_database_to_disk)

    # Begin the loop
    try:
        app.update()
        root.mainloop()
    finally:
        print("Exiting...")


if __name__ == '__main__':
    import sys
    main(sys.argv)
