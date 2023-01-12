#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: chickenpi.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-In Libraries
import atexit
import os
import sys
from tkinter import Tk  # Tk for display window

# 3rd Party Libraries

# Internal Imports
from chicken.control import ControlWindow

# ===================================================================#
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


def entry_point():
    """entry_point

    _extended_summary_
    """
    main(sys.argv)


if __name__ == "__main__":
    main(sys.argv)
