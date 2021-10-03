# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import datetime

# 3rd Party Libraries
from astropy.table import Table

# Internal Imports


class ChickenDatabase():
    """ChickenDatabase Database class for the Chicken-Pi

    [extended_summary]
    """
    def __init__(self):
        # Set up internal variables
        now = datetime.datetime.now()
        self.date = now
        print(f"New database initialized: {now.date()} {now.time()}")

        # Check for existing FITS file for today -- read in or create new

    def read_table_from_fits(self, date):
        """read_table_from_fits [summary]

        [extended_summary]

        Parameters
        ----------
        date : [type]
            [description]
        """


    def add_row_to_table(self, nowobj, sensors, relays, network):
        """add_row_to_table [summary]

        [extended_summary]

        Parameters
        ----------
        nowobj : [type]
            [description]
        sensors : [type]
            [description]
        relays : [type]
            [description]
        network : [type]
            [description]
        """
        print(f"We're adding a row to the database at {nowobj.time()}...")

        row = {}

        # Add the date/time to the row
        row['date'] = nowobj.strftime("%Y-%m-%d")
        row['time'] = nowobj.strftime("%H:%M:%S")

        # Add the sensor readings to the row
        for name in sensors.keys():
            # Retrieve the data from this sensor
            data = sensors[name].data_entry

            # If `data` is a tuple, it's a TH sensor, otherwise a LUX
            if isinstance(data, tuple):
                row[f"{name}_temp"] = data[0]
                row[f"{name}_humid"] = data[1]
            else:
                row[f"{name}_lux"] = data

        # Add the relay status to the row
        for i, state in enumerate(relays.state, 1):
            row[f"outlet_{i}"] = state

        # Add network status to the row
        row['wifi_status'] = network.wifi_status
        row['inet_status'] = network.inet_status
        row['lan_ipv4'] = network.lan_ipv4
        row['wan_ipv4'] = network.wan_ipv4

        print(row)


    def write_table_to_fits(self):
        """write_table_to_fits [summary]

        [extended_summary]
        """

    def get_recent_weather(self, time_range=24):
        """get_recent_weather [summary]

        [extended_summary]

        Parameters
        ----------
        time_range : int, optional
            [description], by default 24
        """


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