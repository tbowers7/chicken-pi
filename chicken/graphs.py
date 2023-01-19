# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: graphs.py

Graphs display window, updates occasionally with current values

"""

# Built-In Libraries
import datetime
import logging
import threading
import tkinter as tk

# 3rd Party Libraries
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.dates import DateFormatter, DayLocator, HourLocator
import matplotlib.pyplot as plt
from noaa_sdk import noaa

# Internal Imports
from chicken import utils

# Geometry
matplotlib.use("TkAgg")


class GraphsWindow:
    """Graphs Window Class

    Creates the graphs window and updates it from time to time.

    Parameters
    ----------
    master : :obj:`tkinter.Tk`
        The master Tk object
    logger : :obj:`logging.Logger`
        The logging object into which to place logging messages
    config : dict
        The configuration file dictionary
    """

    def __init__(self, master, logger: logging.Logger, config: dict, database):

        # Set logger & config as attributes
        self.logger = logger
        self.config = config
        self.geom = self.config["window_geometry"]
        self.data = database

        # Set up window layout as a dictionary
        self.layout = {
            "bkg_color": "#002D04",  # Dark Forest Green
            "fg_color": "#faebd7",  # Antique White
            "font_size": 9,
        }

        # Define the MASTER for the window, set geometry
        # NOTE: Geomtery is set as "X x Y + X0 + Y0"
        self.master = master
        y_0 = (
            self.geom["PI_TOOLBAR"]
            + self.geom["TK_HEADER"]
            + self.geom["STATUS_HIGH"]
            + self.geom["GAP"]
        )
        self.master.geometry(
            f"{self.geom['GRAPHS_WIDE']}x{self.geom['GRAPHS_HIGH']}+"
            f"{self.geom['CONTROL_WIDE']+self.geom['GAP']}+{y_0}"
        )
        self.master.title("Graphs Window")
        self.master.configure(bg=self.layout["bkg_color"])

        # A "frame" holds the various window contents
        self.frame = tk.Frame(self.master, bg=self.layout["bkg_color"])
        self.frame.pack(expand=0)

        # Load the local coordinates from file
        self.lat = self.config["geography"]["latitude"]
        self.lon = self.config["geography"]["longitude"]

        # Create the NOAA object instance
        self.n = noaa.NOAA()
        self.have_forecast = False

        # Plot date formats
        self.alldays = DayLocator()
        self.quartdays = HourLocator(byhour=[0, 6, 12, 18])
        self.dayFormat = DateFormatter("%a %-m/%d")

        # Initialize other attributes
        self.highTemp = None
        self.highDate = None
        self.lowTemp = None
        self.lowDate = None

    def close_window(self):
        """close_window _summary_

        _extended_summary_
        """
        self.master.destroy()

    def get_forecast(self):
        """get_forecast _summary_

        _extended_summary_
        """
        try:
            forecast = self.n.points_forecast(self.lat, self.lon, hourly=False)
        except Exception as error:
            print(error)
            self.have_forecast = False
            return

        nperiods = len(forecast["properties"]["periods"])
        highTemp = []
        highDate = []
        lowTemp = []
        lowDate = []

        for x in range(0, nperiods):

            # For <= 3.6 compatibility, remove colon in time zone
            startTime = forecast["properties"]["periods"][x]["startTime"]
            startTZcol = startTime.rindex(":")
            endTime = forecast["properties"]["periods"][x]["endTime"]
            endTZcol = endTime.rindex(":")

            startBlock = datetime.datetime.strptime(
                startTime[:startTZcol] + startTime[startTZcol + 1 :],
                "%Y-%m-%dT%H:%M:%S%z",
            )
            endBlock = datetime.datetime.strptime(
                endTime[:endTZcol] + endTime[endTZcol + 1 :], "%Y-%m-%dT%H:%M:%S%z"
            )
            midpoint = startBlock + (endBlock - startBlock) / 2

            if forecast["properties"]["periods"][x]["isDaytime"]:
                highTemp.append(forecast["properties"]["periods"][x]["temperature"])
                highDate.append(midpoint)
            else:
                lowTemp.append(forecast["properties"]["periods"][x]["temperature"])
                lowDate.append(midpoint)

        self.highTemp = highTemp
        self.highDate = highDate
        self.lowTemp = lowTemp
        self.lowDate = lowDate

        self.have_forecast = True

    def update(self, now):
        """update _summary_

        _extended_summary_

        Parameters
        ----------
        now : _type_
            _description_
        """
        return
        x = threading.Thread(target=self.get_forecast, daemon=True)
        x.start()
        print(self.have_forecast)
        print("Got here 0?")

        if self.have_forecast:
            plt.close()
            f = plt.Figure(figsize=(5, 5), dpi=100)
            a = f.add_subplot(111)
            # a.xaxis.set_major_locator(self.alldays)
            # a.xaxis.set_minor_locator(self.quartdays)
            a.xaxis.set_major_formatter(self.dayFormat)
            a.grid(which="major", axis="x", color="#505050", linestyle="-")
            # a.grid(which='minor',axis='x',color='pink',linestyle='-')
            a.plot(self.highDate, self.highTemp, "ro")
            a.plot(self.lowDate, self.lowTemp, "bo")
            a.plot(self.highDate, self.highTemp, "r-")
            a.plot(self.lowDate, self.lowTemp, "b-")

            print("Got here 1?")
            canvas = FigureCanvasTkAgg(f, self.master)
            print("Got here 1a?")
            canvas.draw()
            print("Got here 1b?")
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

            print("Got here 2?")
            toolbar = NavigationToolbar2Tk(canvas, self.master)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
