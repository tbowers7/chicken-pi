# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.#
#
#  Created on 10-Apr-2022
#
#  @author: tbowers

"""
  MODULE: monitor_pi.chicken
  FILE: main.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-In Libraries
import atexit
import os
from tkinter import Tk      # Tk for display window

# 3rd Party Libraries
from pkg_resources import resource_filename

# Internal Imports
from .control import ControlWindow


#===================================================================#
def main(args=None):
    """
    Main function
    """
    base_dir = resource_filename('monitor_pi','.')

    root = Tk()
    app = ControlWindow(root, base_dir)
    atexit.register(app.write_database_to_disk)

    # Begin the loop
    try:
        app.update()
        root.mainloop()
    finally:
        print("Exiting...")
