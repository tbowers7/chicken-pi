# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import datetime
from os.path import exists

# 3rd Party Libraries
from astropy.table import Table, vstack

# Internal Imports


class ChickenDatabase():
    """ChickenDatabase Database class for the Chicken-Pi

    [extended_summary]
    """
    def __init__(self):
        # Set up internal variables
        now = datetime.datetime.now()
        self.date = now
        print(f"Chicken-Pi database initialized: {now.date()} {now.time()}")

        # Check for existing FITS file for today -- read in or create new
        today_fn = f"data/coop_{now.strftime('%Y%m%d')}.fits"
        self.table = self.read_table_file() if exists(today_fn) else Table()

    def read_table_file(self, date=None):
        """read_table_file Read the current table in from disk

        [extended_summary]

        Parameters
        ----------
        date : `str`, optional
            The YYMMDD string of the date to read in. [Default: None]

        Returns
        -------
        `astropy.table.Table`
            The table associated with the date
        """
        date = datetime.datetime.now().strftime('%Y%m%d') if date is None \
            else date
        return Table.read(f"data/coop_{date}.fits")

    def add_row_to_table(self, nowobj, sensors, relays, network, debug=False):
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
        debug : `bool`, optional
            Print debugging statements?  [Default: False]
        """
        if debug:
            print(f"We're adding a row to the database at {nowobj.time()}...")

        # Create the empty row dictionary
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

        # Before appending the row to the end of the table, check new day
        #  If so, write out existing table and start a new one
        if 'date' in self.table.colnames and \
            row['date'] != self.table['date'][-1]:
            self.write_table_to_fits()
            self.table = Table()

        # Append the row to the end of the table
        self.table = vstack([self.table, row])
        if debug:
            self.table.pprint()

    def write_table_to_fits(self, date=None):
        """write_table_to_fits [summary]

        [extended_summary]

        Parameters
        ----------
        date : `str`, optional
            The YYMMDD string of the date to read in. [Default: None]
        """
        if date is None:
            dt_object = datetime.datetime.now() - datetime.timedelta(minutes=15)
            date = dt_object.strftime('%Y%m%d')
        self.table.write(f"data/coop_{date}.fits", overwrite=True)

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