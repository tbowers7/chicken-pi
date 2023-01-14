# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: main.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-In Libraries
import atexit
import sys
import tkinter as tk

# 3rd Party Libraries

# Internal Imports
from chicken.control import ControlWindow

# ===================================================================#
def main(args):
    """
    Main function
    """
    root = tk.Tk()
    app = ControlWindow(root)
    atexit.register(app.write_database_to_disk)

    # Begin the loop
    try:
        app.update()
        root.mainloop()
    finally:
        print("Exiting...")

    return 0


def entry_point():
    """entry_point

    _extended_summary_
    """
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
