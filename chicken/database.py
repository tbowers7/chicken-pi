# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import atexit
import datetime

# 3rd Party Libraries
from astropy.table import Table
import numpy as np

# Internal Imports


class ChickenDatabase():

    def __init__(self):
        # Set up internal variables
        now = datetime.datetime.now()
        self.date = now
        print(f"New database initialized: {now.date()} {now.time()}")

        # Check for existing FITS file for today -- read in or create new
        
        pass

    def read_table_from_fits(self, date):
        pass

    def add_row_to_table(self, nowobj, sensors, relays, other):
        print(f"We're adding a row to the database at {nowobj.time()}...")
        pass

    def write_table_to_fits(self):
        pass

    def get_recent_weather(self, range=24):
        pass



'''
Outline:
    Daily make a new Table to hold observations
    Record everything we want to every 5 mintues
    At end of day (or at exit) write the Table to FITS in data/ directory

Provide routines to:
    Read in extant file for the day
    Add lines to the table
    Write out the Table to FITS
    Retrieve information from the Table for graphing routines
'''