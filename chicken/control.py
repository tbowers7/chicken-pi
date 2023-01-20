# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: control.py

Control window, with all the shiny knobs and buttons

"""

# Built-In Libraries
import datetime
import logging
import tkinter as tk

# 3rd Party Libraries
import numpy as np

# Internal Imports
from chicken.database import ChickenDatabase, OperationalSettings
from chicken.graphs import GraphsWindow
from chicken.network import NetworkStatus
from chicken.status import StatusWindow, LogWindow
from chicken import utils

try:
    from chicken.device import set_up_sensors, Relay
except ModuleNotFoundError:
    from chicken.dummy import set_up_sensors, Relay


class ControlWindow:
    """Control Window Class

    Creates the main control window and also spawns the secondary display
    windows.

    Parameters
    ----------
    master : :obj:`tkinter.Tk`
        The master Tk object
    logger : :obj:`logging.Logger`
        The logging object into which to place logging messages
    """

    def __init__(self, master, logger: logging.Logger):

        # Set logger as attribute; set after_id
        self.logger = logger
        self.after_id = None

        # Set up window layout as a dictionary
        self.layout = {
            "outlet_row": 2,  # Start of the Outlet Section
            "bkg_color": "lightgreen",  # Background color of the Control Window
        }
        # Start of the Door Section
        self.layout["door_row"] = self.layout["outlet_row"] + 14

        # Load the configuration file
        self.config = utils.load_yaml_config()
        self.geom = self.config["window_geometry"]

        # Initialize sensors and relays
        self.sensors = set_up_sensors()
        self.relays = Relay()

        # Set up the database and network status classes
        self.network = NetworkStatus(self.logger)
        self.database = ChickenDatabase(self.logger)

        # Indicator LEDs
        self.led = {
            "on": tk.PhotoImage(
                file=utils.Paths.resources.joinpath("green-led-on-th.png")
            ),
            "off": tk.PhotoImage(
                file=utils.Paths.resources.joinpath("green-led-off-th.png")
            ),
        }

        # Define the MASTER for the CONTROL window, and spawn the other windows
        self.master = master
        self.status_window = StatusWindow(
            tk.Toplevel(self.master), self.logger, self.config
        )
        self.log_window = LogWindow(tk.Toplevel(self.master), self.logger, self.config)
        self.graphs_window = GraphsWindow(
            tk.Toplevel(self.master), self.logger, self.config, self.database
        )

        # Define the geometry and title for the CONTROL window
        # NOTE: Geomtery is set as "X x Y + X0 + Y0"
        self.master.geometry(
            f"{self.geom['CONTROL_WIDE']}x{self.geom['CONTROL_HIGH']}+"
            f"0+{self.geom['PI_TOOLBAR']}"
        )
        self.master.title("Control Window")
        self.master.configure(bg=self.layout["bkg_color"])

        ## A "frame" holds the various GUI controls
        self.frame = tk.Frame(self.master)
        self.frame.pack(expand=1, fill=tk.BOTH)

        # ===== SWITCHED OUTLETS =====#
        tk.Label(
            self.frame,
            text="Relay-Controlled Outlets",
            fg="darkblue",
            bg="#ffff80",
            font=("courier", 14, "bold"),
        ).grid(
            row=self.layout["outlet_row"] - 1,
            column=0,
            columnspan=4,
            sticky=tk.W + tk.E,
        )

        # The outlets are held as a list of OutletControl object instances
        self.outlet = []
        for i, name in enumerate(self.config["outlets"].values()):
            params = {
                "name": name,
                "column": i,
                "sensors": self.sensors,
                "img": self.led["off"],
                "geom": self.geom,
                "layout": self.layout,
            }
            self.outlet.append(OutletControl(self.frame, params))

        # ===== DOOR =====#
        tk.Label(self.frame, text=" - " * 40, fg="darkblue").grid(
            row=self.layout["door_row"] - 1, column=0, columnspan=4, sticky=tk.W + tk.E
        )
        tk.Label(
            self.frame,
            text="Automated Chicken Door",
            fg="darkblue",
            bg="#ffff80",
            font=("courier", 14, "bold"),
        ).grid(row=self.layout["door_row"], column=0, columnspan=4, sticky=tk.W + tk.E)

        self.door = DoorControl(
            self.frame,
            {"sensors": self.sensors, "geom": self.geom, "layout": self.layout},
        )

        # Set up the 'SaveSettings' object
        self.settings = OperationalSettings(self.outlet, self.door)

    def update(self):
        """Update the display windows

        This method updates information in all windows, not just the CONTROL
        window.  To minimize overuse of the I2C bus and spurious switching
        of the relays, various delays are included here.  For instance:
            * The relays are only set at the top of every minute
            * The status is written to the database once a minute
        """
        # This is the official time for Chicken Pi
        now = datetime.datetime.now()

        # Check for changes in the GUI settings
        self.settings.check_for_change(self.outlet, self.door)

        # Every 60 seconds, write changes in relay command to relays
        if now.second % 60 == 0:
            self.set_relays()

        # Update status window each time through the method
        self.status_window.update(now, self.sensors, self.relays, self.network)

        # Update the LED status indicators in the CONTROL Window
        for outlet in self.outlet:
            outlet.img = self.led["on" if outlet.state else "off"]
            outlet.command_led.configure(image=outlet.img)

        # Every minute, write status to database
        if now.second % 60 == 0:  # and now.minute % 1 == 0:
            self.write_to_database(now)
            self.log_window.update()
            # Update the Graphs window
            self.graphs_window.plot_data()

        # Wait 0.5 seconds (500 ms) and repeat
        self.after_id = self.master.after(500, self.update)

    def set_relays(self, change=False):
        """Write the relay commands to the Relay HAT

        _extended_summary_

        Parameters
        ----------
        change : bool, optional
            Did anything change? (Default: False)
        """
        # Check to see if any states have changed
        for i, outlet in enumerate(self.outlet):
            demand = outlet.demand  # Call just once, since this queries I2C
            if self.relays.state[i] != demand:
                self.relays.state[i] = demand
                change = True

        # If anything changed, write the new values to the relat HAT
        # NOTE: The relay scheme of state[i] being the canonical knowledge of
        #  the relay status (read just isn't working) means that the write
        #  MUST be successful else the actual relay state won't be known to
        #  the rest of the program.
        if change:
            self.relays.good_write = False
            while not self.relays.good_write:
                # Warning: This could lead to an infinite loop?
                self.relays.write()

    def write_to_database(self, now, verbose=False):
        """Write the current status readings to the database

        [extended_summary]

        Parameters
        ----------
        now : :obj:`datetime.datetime`
            The current time object, for including in the database
        verbose : bool, optional
            Provide verbose output?  (Default: False)
        """
        logger_level = self.logger.info if verbose else self.logger.debug
        logger_level("Writing readings to the database...")
        self.database.add_row_to_table(now, self.sensors, self.relays, self.network)

    def write_database_to_disk(self):
        """Write the entire database to disk

        Write the database from memory onto disk for long-term preservation
        """
        # Write the current status to the database first
        self.write_to_database(datetime.datetime.now())
        self.database.write_table_to_fits()


class _BaseControl:
    """Base class for Object Control

    This base class contains the various common components for both the
    outlets and the door (and possibly other components to be added in
    the future.)
    """

    def __init__(self):
        # Initialize the various variables required
        self.enable = False  # Switch Enabled
        self.and_or = False  # Time AND/OR Temperature
        self.on_time = 0  # Switch turn on time
        self.off_time = 0  # Switch turn off time
        self.switch_temp = 20  # Temp / Light trigger for switch
        self.temp_direction = 0  # Temperature direction for trigger
        self.en_var = tk.BooleanVar()  # Variable needed for ENABLE boxes
        self.tempsel_var = tk.IntVar()  # Variable needed for temp radio button
        self.andor_var = tk.BooleanVar()  # Variable needed for the ... ?
        self.time_cycle = 0  # Time cycle: ON or ON-OFF-ON or OFF-ON-OFF
        self.on_label = None  # Dummy -- To be created by inheriting class
        self.off_label = None  # Dummy -- To be created by inheriting class

    # Various Update Methods
    def update_enable(self):
        """Update the ENABLE state for this device from the GUI"""
        self.enable = self.en_var.get()

    def update_on_time(self, seltime):
        """Update the turn-on time for this device from the GUI

        Parameters
        ----------
        seltime : string or float
            The selected time from the Tk widget
        """
        self.on_time = float(seltime)
        self.on_label.config(text=f" ON {self.string_time(self.on_time)}")
        self.update_time_cycle()

    def update_off_time(self, seltime):
        """Update the turn-off time for this device from the GUI

        Parameters
        ----------
        seltime : string or float
            The selected time from the Tk widget
        """
        self.off_time = float(seltime)
        self.off_label.config(text=f" OFF {self.string_time(self.off_time)}")
        self.update_time_cycle()

    def update_time_cycle(self):
        """Update the time cycle for this device

        The "time cycle" is a way of parameterizing the cyclic nature of a
        day onto a linear 24-hour line:
            0: On time == Off time, always on
            1: On at midnight, off during the day, on again before midnight
            2: Off at midnight, on during the day, off again before midnight
        """
        if self.on_time == self.off_time or abs(self.on_time - self.off_time) == 24:
            self.time_cycle = 0  # ON always
        elif self.on_time > self.off_time:
            self.time_cycle = 1  # ON - OFF - ON
        else:
            self.time_cycle = 2  # OFF - ON - OFF

    @staticmethod
    def string_time(in_time):
        """Create a printable time string for the slider bar

        Parameters
        ----------
        in_time : float
            Input time from the Tk widget

        Returns
        -------
        str
            The formatted string
        """
        hour, minute = (
            int(in_time),
            60 * (in_time % 1),
        )  # Compute minutes from in_time
        hour = 0 if hour == 24 else hour  # Catch case of 24:00
        ampm = "PM" if hour >= 12 else "AM"  # Set PM/AM times
        if hour >= 12:
            hour -= 12
        hour = 12 if hour == 0 else hour  # Catch case of 0:00
        return f"{hour:2d}:{int(minute):0>2d} {ampm}"

    @staticmethod
    def string_temp(in_temperature):
        """Create a printable temperature string for the slider bar

        Parameters
        ----------
        in_temperature : float
            Input temperature from the Tk widget

        Returns
        -------
        str
            The formatted string
        """
        return f"{int(in_temperature):2d}\N{DEGREE SIGN} F"

    @staticmethod
    def string_light(in_log_lux):
        """Create a printable light level string for the slider bar

        Parameters
        ----------
        in_log_lux : float
            Input log lux from the Tk widget

        Returns
        -------
        str
            The formatted string
        """
        display_lux = 10**in_log_lux
        # Round to make look pretty
        display_lux = (
            np.round(display_lux / 10.0) * 10.0
            if display_lux < 1000
            else np.round(display_lux / 100.0) * 100.0
        )
        return f"{display_lux:,.0f} lux"


class OutletControl(_BaseControl):
    """Outlet control class

    _extended_summary_

    Parameters
    ----------
    frame : :obj:`tkinter.Frame`
        The frame object into which to place these controls
    params : dict
        Dictionary containing the various parameters needed
    """

    def __init__(self, frame, params):
        super().__init__()
        self.sensors = params["sensors"]

        # Unpack repeatedly used params members:
        column = params["column"]
        outlet_row = params["layout"]["outlet_row"]
        self.img = params["img"]

        # Scale slider width to window
        slider_size = (params["geom"]["CONTROL_WIDE"] - 5 * 5) / 4

        # Column Label for this outlet
        tk.Label(frame, text=f"{params['name']} (#{column+1})", bg="#f0f0f0").grid(
            row=outlet_row + 1, column=column, sticky=tk.W + tk.E
        )

        # Individual Labels:
        self.on_label = tk.Label(
            frame,
            fg="green",
            bg="#e0ffe0",
            text=f" ON {self.string_time(self.on_time)}",
        )
        self.off_label = tk.Label(
            frame,
            fg="red",
            bg="#ffe0e0",
            text=f" OFF {self.string_time(self.off_time)}",
        )
        self.temp_label = tk.Label(
            frame,
            fg="blue",
            bg="#e0e0ff",
            text=f" Coop Temp {self.string_temp(self.switch_temp)}",
        )

        # Enable Box
        self.enable_box = tk.Checkbutton(
            frame,
            text="Enable",
            variable=self.en_var,
            command=self.update_enable,
            onvalue=True,
            offvalue=False,
        )

        # Sliders
        self.on_slider = tk.Scale(
            frame,
            from_=0,
            to=24,
            digits=4,
            orient=tk.HORIZONTAL,
            resolution=0.25,
            command=self.update_on_time,
            variable=tk.DoubleVar,
            length=slider_size,
            showvalue=0,
            troughcolor="#bfd9bf",
        )
        self.off_slider = tk.Scale(
            frame,
            from_=0,
            to=24,
            digits=4,
            orient=tk.HORIZONTAL,
            resolution=0.25,
            command=self.update_off_time,
            variable=tk.DoubleVar,
            length=slider_size,
            showvalue=0,
            troughcolor="#d9bfbf",
        )
        self.temp_slider = tk.Scale(
            frame,
            from_=20,
            to=80,
            digits=2,
            orient=tk.HORIZONTAL,
            resolution=5,
            command=self.update_temp_trigger,
            variable=tk.IntVar,
            length=slider_size,
            showvalue=0,
            troughcolor="#bfbfd9",
        )

        # AND/OR Buttons
        self.and_or_frame = tk.Frame(frame)
        self.and_button = tk.Radiobutton(
            self.and_or_frame,
            indicatoron=0,
            value=True,
            text="   AND   ",
            variable=self.andor_var,
            command=self.update_andor,
            bg="#e0e0e0",
            selectcolor="#50C878",
        )
        self.or_button = tk.Radiobutton(
            self.and_or_frame,
            indicatoron=0,
            value=False,
            text="   OR   ",
            variable=self.andor_var,
            command=self.update_andor,
            bg="#e0e0e0",
            selectcolor="#50C878",
        )

        # Temperature Direction Radio Buttons
        self.no_temp_button = tk.Radiobutton(
            frame,
            fg="blue",
            bg="#f0f0ff",
            value=0,
            command=self.update_temp_direction,
            variable=self.tempsel_var,
            anchor=tk.W,
            text="Temp independent",
            font=("", 9),
        )
        self.up_temp_button = tk.Radiobutton(
            frame,
            fg="blue",
            bg="#f0f0ff",
            value=1,
            command=self.update_temp_direction,
            variable=self.tempsel_var,
            anchor=tk.W,
            text="Turn ON above: ",
        )
        self.down_temp_button = tk.Radiobutton(
            frame,
            fg="blue",
            bg="#f0f0ff",
            value=-1,
            command=self.update_temp_direction,
            variable=self.tempsel_var,
            anchor=tk.W,
            text="Turn ON below:",
        )

        self.command_led = tk.Label(frame, image=self.img)

        # Set everything to the grid
        self.on_label.grid(row=outlet_row + 3, column=column, sticky=tk.W + tk.E)
        self.off_label.grid(row=outlet_row + 5, column=column, sticky=tk.W + tk.E)
        self.temp_label.grid(row=outlet_row + 11, column=column, sticky=tk.W + tk.E)
        self.enable_box.grid(row=outlet_row + 2, column=column)
        self.on_slider.grid(row=outlet_row + 4, column=column, sticky=tk.W + tk.E)
        self.off_slider.grid(row=outlet_row + 6, column=column, sticky=tk.W + tk.E)
        self.temp_slider.grid(row=outlet_row + 12, column=column, sticky=tk.W + tk.E)
        self.and_or_frame.grid(row=outlet_row + 7, column=column, sticky=tk.W + tk.E)
        self.and_button.pack(side=tk.LEFT, expand=1)
        self.or_button.pack(side=tk.LEFT, expand=1)
        self.no_temp_button.grid(row=outlet_row + 8, column=column, sticky=tk.W + tk.E)
        self.up_temp_button.grid(row=outlet_row + 9, column=column, sticky=tk.W + tk.E)
        self.down_temp_button.grid(
            row=outlet_row + 10, column=column, sticky=tk.W + tk.E
        )
        self.command_led.grid(row=outlet_row, column=column, sticky=tk.W + tk.E)

    def update_temp_trigger(self, seltemp):
        """Update the temperature trigger point

        Parameters
        ----------
        seltemp : float
            Selected temperature from the Tk widget
        """
        self.switch_temp = int(seltemp)
        self.temp_label.config(text=f" Coop Temp {self.string_temp(self.switch_temp)}")

    def update_andor(self):
        """Update the AND/OR flag for tempature/time"""
        self.and_or = self.andor_var.get()

    def update_temp_direction(self):
        """Update the temperature trigger direction"""
        self.temp_direction = self.tempsel_var.get()

    def cmd_state(self, nowobj, use_cache=False):
        """Construct the commanded state from the control knobs

        [extended_summary]

        Parameters
        ----------
        nowobj : :obj:`datetime.datetime`
            The output of ``datetime.datetime.now()``
        use_cache : bool, optional
            Use the cached sensor values rather thsn checking? (Default: False)

        Returns
        -------
        bool
            Should the device be on or off?
        """
        # If 'ENABLE' box not checked, keep off
        if not self.enable:
            return False

        # Get time commanded state
        nowh = nowobj.hour + nowobj.minute / 60.0 + nowobj.second / 3600.0
        # ON-OFF-ON
        if self.time_cycle == 1:
            timecmd = not self.off_time <= nowh < self.on_time
        # OFF-ON-OFF
        elif self.time_cycle == 2:
            timecmd = self.on_time <= nowh < self.off_time
        # Always ON
        else:
            timecmd = True

        # Get temperature commanded state
        intemp = (
            self.sensors["inside"].temp
            if not use_cache
            else self.sensors["inside"].cache_temp
        )
        # ON above
        if self.temp_direction == 1:
            tempcmd = intemp > self.switch_temp
        # ON below
        elif self.temp_direction == -1:
            tempcmd = intemp < self.switch_temp
        # Temperature Independent
        else:
            tempcmd = None

        # Combine using AND/OR
        if tempcmd is None:
            return timecmd
        return timecmd and tempcmd if self.and_or else timecmd or tempcmd

    @property
    def demand(self):
        """Return the demanded state as a class attribute

        Returns
        -------
        bool
            The current demanded state of the device
        """
        return self.cmd_state(datetime.datetime.now())

    @property
    def state(self):
        """Return the cached state as a class attribute

        Returns
        -------
        bool
            The current (cached) state of the device
        """
        return self.cmd_state(datetime.datetime.now(), use_cache=True)


class DoorControl(_BaseControl):
    """Door control class

    _extended_summary_

    Parameters
    ----------
    frame : :obj:`tkinter.Frame`
        The frame object into which to place these controls
    params : dict
        Dictionary containing the various parameters needed
    """

    def __init__(self, frame, params):
        super().__init__()
        self.sensors = params["sensors"]

        # Unpack repeatedly used params members:
        door_row = params["layout"]["door_row"]

        # Scale slider width to window
        slider_size = (params["geom"]["CONTROL_WIDE"] - 5 * 5) / 4

        # Column 0: ENABLE
        self.door_enable = tk.Checkbutton(
            frame,
            text="Enable",
            onvalue=True,
            offvalue=False,
            variable=self.en_var,
            command=self.update_enable,
            state=tk.DISABLED,
        )

        # Column 1: Open Time
        self.on_label = tk.Label(
            frame,
            fg="green",
            bg="#e0ffe0",
            text=f" OPEN {self.string_time(self.on_time)}",
        )
        self.door_open_slider = tk.Scale(
            frame,
            from_=0,
            to=24,
            digits=4,
            orient=tk.HORIZONTAL,
            resolution=0.25,
            command=self.update_open_time,
            showvalue=0,
            variable=tk.DoubleVar,
            length=slider_size,
            troughcolor="#bfd9bf",
        )

        # Column 2: Close Time
        self.off_label = tk.Label(
            frame,
            fg="red",
            bg="#ffe0e0",
            text=f" CLOSE {self.string_time(self.off_time)}",
        )
        self.door_closed_slider = tk.Scale(
            frame,
            from_=0,
            to=24,
            digits=4,
            orient=tk.HORIZONTAL,
            resolution=0.25,
            command=self.update_close_time,
            showvalue=0,
            variable=tk.DoubleVar,
            length=slider_size,
            troughcolor="#d9bfbf",
        )

        # Column 3: Light Trigger
        self.switch_temp = 2
        self.door_light_label = tk.Label(
            frame,
            fg="#9932cc",
            bg="#f3e6f9",
            text=f" LIGHT {self.string_light(self.switch_temp)}",
        )
        self.door_light_slider = tk.Scale(
            frame,
            from_=2,
            to=4,
            digits=4,
            orient=tk.HORIZONTAL,
            resolution=0.05,
            command=self.update_door_light,
            showvalue=0,
            variable=tk.DoubleVar,
            length=slider_size,
            troughcolor="#cfc4d4",
        )

        # Set everything to the grid
        self.door_enable.grid(row=door_row + 1, column=0, rowspan=2)
        self.on_label.grid(row=door_row + 1, column=1, sticky=tk.W + tk.E)
        self.door_open_slider.grid(row=door_row + 2, column=1, sticky=tk.W + tk.E)
        self.off_label.grid(row=door_row + 1, column=2, sticky=tk.W + tk.E)
        self.door_closed_slider.grid(row=door_row + 2, column=2, sticky=tk.W + tk.E)
        self.door_light_label.grid(row=door_row + 1, column=3, sticky=tk.W + tk.E)
        self.door_light_slider.grid(row=door_row + 2, column=3, sticky=tk.W + tk.E)

    # Light Update Method
    def update_door_light(self, sellux):
        """Update the door light trigger

        Parameters
        ----------
        sellux : float
            Selected lux from the Tk widget
        """
        self.switch_temp = float(sellux)
        self.door_light_label.config(
            text=f" LIGHT > {self.string_light(self.switch_temp)}"
        )

    def update_open_time(self, seltime):
        """Update the open time for the door from the GUI

        Parameters
        ----------
        seltime : string or float
            The selected time from the Tk widget
        """
        self.on_time = float(seltime)
        self.on_label.config(text=f" OPEN {self.string_time(self.on_time)}")
        self.update_time_cycle()

    def update_close_time(self, seltime):
        """Update the close time for the door from the GUI

        Parameters
        ----------
        seltime : string or float
            The selected time from the Tk widget
        """
        self.off_time = float(seltime)
        self.off_label.config(text=f" CLOSE {self.string_time(self.off_time)}")
        self.update_time_cycle()
