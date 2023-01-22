# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: graphs.py

Graphs display window, updates occasionally with current values

"""

# Built-In Libraries
import logging

# import threading
import tkinter as tk

# 3rd Party Libraries
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, ConciseDateFormatter, AutoDateLocator
import matplotlib.pyplot as plt
from noaa_sdk import noaa

# Internal Imports
from chicken.database import ChickenDatabase

# Geometry
matplotlib.use("TkAgg")


class GraphsWindow:
    """Graphs Window Class

    Creates the graphs window and updates it from time to time.

    .. note::
        Window geomtery is set as "X x Y + X0 + Y0"

    Parameters
    ----------
    master : :obj:`tkinter.Tk`
        The master Tk object
    logger : :obj:`logging.Logger`
        The logging object into which to place logging messages
    config : dict
        The configuration file dictionary
    """

    def __init__(
        self, master, logger: logging.Logger, config: dict, database: ChickenDatabase
    ):

        # Set logger & config as attributes
        self.logger = logger
        self.config = config
        self.geom = self.config["window_geometry"]
        self.data = database

        # Set up window layout as a dictionary
        self.layout = {
            "bkg_color": "#002D04",  # Dark Forest Green
            "fg_color": "#faebd7",  # Antique White
            "font_size": 8,
        }

        # Define the MASTER for the window, set geometry
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
        self.noaa = noaa.NOAA() if self.config["use_nws"] else None
        self.have_forecast = False

        # Plot date formats
        # self.alldays = DayLocator()
        # self.quartdays = HourLocator(byhour=[0, 6, 12, 18])
        self.day_format = DateFormatter("%a %-m/%d")

        # Define instance attributes needed for the plotting
        self.ax1 = None
        self.canvas = None
        self.tsz = 8

        # Create the plot setup
        self.create_plot()

        # Create the lookback info
        self.lookback = 1
        tk.Label(
            self.frame,
            text="Lookback Time:",
            fg=self.layout["fg_color"],
            bg=self.layout["bkg_color"],
        ).grid(row=0, column=0, sticky=tk.W + tk.E)
        slider_size = self.geom["GRAPHS_WIDE"] * 0.50
        self.lookback_slider = tk.Scale(
            self.frame,
            from_=1,
            to=7,
            digits=1,
            orient=tk.HORIZONTAL,
            resolution=1,
            command=self.update_lookback,
            variable=tk.DoubleVar,
            length=slider_size,
            showvalue=0,
            troughcolor="#547857",
            bg=self.layout["bkg_color"],
            fg=self.layout["fg_color"],
            highlightcolor=self.layout["fg_color"],
        )
        self.lookback_label = tk.Label(
            self.frame,
            fg=self.layout["fg_color"],
            bg=self.layout["bkg_color"],
            text=f" {self.lookback} day{'s' if self.lookback > 1 else ' '} ",
        )
        self.lookback_set = tk.Button(
            self.frame,
            command=self.plot_data,
            text="Set",
            bg="#547857",
            fg=self.layout["fg_color"],
            activebackground=self.layout["fg_color"],
            activeforeground=self.layout["bkg_color"],
        )

        # Set lookback stuff to the grid
        self.lookback_slider.grid(row=0, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.lookback_label.grid(row=0, column=3, sticky=tk.W + tk.E)
        self.lookback_set.grid(row=0, column=4, sticky=tk.W + tk.E)

    def close_window(self):
        """close_window _summary_

        _extended_summary_
        """
        self.master.destroy()

    def create_plot(self):
        """Create the plot environment

        _extended_summary_
        """
        # Initialize the figure object and create the axis attribute
        pix_size = 1 / plt.rcParams["figure.dpi"]  # pixel in inches
        figure = plt.figure(
            figsize=(
                self.geom["GRAPHS_WIDE"] * pix_size,
                (self.geom["GRAPHS_HIGH"] - 30) * pix_size,
            )
        )
        self.ax1 = figure.add_subplot(311)
        self.ax1.text(0.5, 0.5, "Graphs will load shortly...", ha="center", va="center")

        self.ax2 = figure.add_subplot(312)
        self.ax3 = figure.add_subplot(313)

        self.axis_list = [self.ax1, self.ax2, self.ax3]
        for axis in self.axis_list:
            axis.tick_params(
                axis="both",
                which="both",
                direction="in",
                top=True,
                right=True,
                labelsize=self.tsz,
            )
        plt.subplots_adjust(hspace=0.0)

        # Create the Tk Canvas object and draw it
        self.canvas = FigureCanvasTkAgg(figure, master=self.frame)
        self.canvas.get_tk_widget().pack()
        self.canvas.get_tk_widget().grid(row=1, columnspan=5)
        self.canvas.draw()

    def plot_data(self):
        """Plot the data in the figure

        _extended_summary_
        """
        # Clear the axis from the previous plot
        for axis in self.axis_list:
            axis.clear()

        # Retrieve the cleaned historical data from the Database object using
        #  the current ``lookback`` time.
        timestamps, data = self.data.retrieve_historical(self.lookback)

        # Start building the plot
        # Temperature Panel
        self.ax1.plot(
            timestamps,
            data["inside_temp"],
            label="Inside Coop",
            linewidth=0.8,
            color="C1",
        )
        self.ax1.plot(
            timestamps,
            data["outside_temp"],
            label="Outside",
            linewidth=0.8,
            color="C2",
        )
        self.ax1.set_ylabel("Temp (\xb0F)", fontsize=self.tsz)
        # self.ax1.set_xlabel("Time", fontsize=self.tsz)
        # self.ax1.xaxis.set_major_formatter(ConciseDateFormatter(AutoDateLocator))
        self.ax1.set_xticklabels([])
        self.ax1.legend(loc="lower left", fontsize=self.tsz)

        # Relative Humidity Panel
        self.ax2.plot(
            timestamps,
            data["inside_humid"],
            label="Inside Coop",
            linewidth=0.8,
            color="C1",
        )
        self.ax2.plot(
            timestamps,
            data["outside_humid"],
            label="Outside",
            linewidth=0.8,
            color="C2",
        )
        self.ax2.set_ylabel("Rel Humid (%)", fontsize=self.tsz)
        # self.ax2.set_xlabel("Time", fontsize=self.tsz)
        # self.ax2.xaxis.set_major_formatter(ConciseDateFormatter(AutoDateLocator))
        self.ax2.set_xticklabels([])
        self.ax2.legend(loc="lower left", fontsize=self.tsz)

        # Light (and WiFi?) panel
        self.ax3.plot(
            timestamps,
            data["light_lux"],
            label="Light Level",
            linewidth=0.8,
            color="C0",
        )
        self.ax3.set_yscale("log")
        self.ax3.set_ylabel("Light (lux)", fontsize=self.tsz)
        self.ax3.set_xlabel("Date / Time", fontsize=self.tsz)
        self.ax3.xaxis.set_major_formatter(ConciseDateFormatter(AutoDateLocator))
        # self.ax3.legend(loc="lower right", fontsize=self.tsz)

        plt.subplots_adjust(hspace=0.0, bottom=0, top=1)
        plt.tight_layout()

        # Draw the new plot into the Canvas
        self.canvas.draw()

    # def get_forecast(self):
    #     """get_forecast _summary_

    #     _extended_summary_
    #     """
    #     try:
    #         forecast = self.n.points_forecast(self.lat, self.lon, hourly=False)
    #     except Exception as error:
    #         print(error)
    #         self.have_forecast = False
    #         return

    #     nperiods = len(forecast["properties"]["periods"])
    #     highTemp = []
    #     highDate = []
    #     lowTemp = []
    #     lowDate = []

    #     for x in range(0, nperiods):

    #         # For <= 3.6 compatibility, remove colon in time zone
    #         startTime = forecast["properties"]["periods"][x]["startTime"]
    #         startTZcol = startTime.rindex(":")
    #         endTime = forecast["properties"]["periods"][x]["endTime"]
    #         endTZcol = endTime.rindex(":")

    #         startBlock = datetime.datetime.strptime(
    #             startTime[:startTZcol] + startTime[startTZcol + 1 :],
    #             "%Y-%m-%dT%H:%M:%S%z",
    #         )
    #         endBlock = datetime.datetime.strptime(
    #             endTime[:endTZcol] + endTime[endTZcol + 1 :], "%Y-%m-%dT%H:%M:%S%z"
    #         )
    #         midpoint = startBlock + (endBlock - startBlock) / 2

    #         if forecast["properties"]["periods"][x]["isDaytime"]:
    #             highTemp.append(forecast["properties"]["periods"][x]["temperature"])
    #             highDate.append(midpoint)
    #         else:
    #             lowTemp.append(forecast["properties"]["periods"][x]["temperature"])
    #             lowDate.append(midpoint)

    #     self.highTemp = highTemp
    #     self.highDate = highDate
    #     self.lowTemp = lowTemp
    #     self.lowDate = lowDate

    #     self.have_forecast = True

    def update(self):
        """update _summary_

        _extended_summary_

        Parameters
        ----------
        now : _type_
            _description_
        """
        # x = threading.Thread(target=self.get_forecast, daemon=True)
        # x.start()
        # print(self.have_forecast)
        # print("Got here 0?")

        # if self.have_forecast:
        #     plt.close()
        #     f = plt.Figure(figsize=(5, 5), dpi=100)
        #     a = f.add_subplot(111)
        #     # a.xaxis.set_major_locator(self.alldays)
        #     # a.xaxis.set_minor_locator(self.quartdays)
        #     a.xaxis.set_major_formatter(self.day_format)
        #     a.grid(which="major", axis="x", color="#505050", linestyle="-")
        #     # a.grid(which='minor',axis='x',color='pink',linestyle='-')
        #     a.plot(self.highDate, self.highTemp, "ro")
        #     a.plot(self.lowDate, self.lowTemp, "bo")
        #     a.plot(self.highDate, self.highTemp, "r-")
        #     a.plot(self.lowDate, self.lowTemp, "b-")

        #     print("Got here 1?")
        #     canvas = FigureCanvasTkAgg(f, self.master)
        #     print("Got here 1a?")
        #     canvas.draw()
        #     print("Got here 1b?")
        #     canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        #     print("Got here 2?")
        #     toolbar = NavigationToolbar2Tk(canvas, self.master)
        #     toolbar.update()
        #     canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_lookback(self, seltime):
        """Update the lookback time from the GUI

        Parameters
        ----------
        seltime : string or float
            The selected time from the Tk widget
        """
        self.lookback = int(seltime)
        self.lookback_label.config(
            text=f" {self.lookback} day{'s' if self.lookback > 1 else ' '} "
        )
