# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: status.py

Status display window, updates frequently with current values

"""

# Built-In Libraries
import tkinter as tk
import time

# 3rd Party Libraries


class StatusWindow:
    """
    StatusWindow class
    Creates the status window and (supposedly) updates it from time to time.
    """

    def __init__(self, master, control_width):
        """
        __init__ method: initializes the Status Window
        """
        # Set up geometry as a dictionary
        self.geom = {
            "PI_TOOLBAR": 36,
            "TK_HEADER": 25,
            "CONTROL_WIDTH": control_width,
            "WIDGET_WIDE": 600,  # Width of the "Status Window"
            "WIDGET_HIGH": 300,  # Height of the "Status Window"
            "STATBG": "black",
            "FONTSIZE": 13,
            "DATAFIELD": 15,  # Width of a data field
            "ENVROW": 1,  # Widget row for environmental status
            "DEVROW": 5,  # Widget row for device status
            "NETROW": 9,  # Widget row for network status
        }

        # Because these are used so often...
        env_row = self.geom["ENVROW"]
        dev_row = self.geom["DEVROW"]
        net_row = self.geom["NETROW"]

        # Define the MASTER for the window, set geometry
        self.master = master
        self.master.geometry(
            f"{self.geom['WIDGET_WIDE']}x{self.geom['WIDGET_HIGH']}+"
            f"{self.geom['CONTROL_WIDTH']+10}+{self.geom['PI_TOOLBAR']}"
        )
        self.master.title("Status Window")
        self.master.configure(bg=self.geom["STATBG"])

        # A "frame" holds the various window contents
        self.frame = tk.Frame(self.master, bg=self.geom["STATBG"])
        self.frame.pack(expand=0)

        # Put the time at the top of the window
        self.display_time = tk.Label(
            self.frame,
            font=("courier", self.geom["FONTSIZE"], "bold"),
            bg=self.geom["STATBG"],
            fg="skyblue",
        )
        self.display_time.grid(row=0, columnspan=4)

        # Create the various section labels
        self.make_section_label("Environmental Status", row=env_row)
        self.make_section_label("Network Status", row=net_row)
        self.make_section_label("Device Status", row=dev_row)

        # Environmental Status Labels
        self.make_statistic_label("    Outside:", row=env_row + 1, column=0)
        self.make_statistic_label("Inside Coop:", row=env_row + 2, column=0)
        self.make_statistic_label("Light Level:", row=env_row + 3, column=0)
        self.make_statistic_label(" Inside Box:", row=env_row + 1, column=2)
        self.make_statistic_label("   RPi4 CPU:", row=env_row + 2, column=2)

        # Environmental Status Data
        self.env_outside_data = self.make_statistic_data(row=env_row + 1, column=1)
        self.env_inside_data = self.make_statistic_data(row=env_row + 2, column=1)
        self.env_light_data = self.make_statistic_data(row=env_row + 3, column=1)
        self.env_pi_data = self.make_statistic_data(row=env_row + 1, column=3)
        self.env_cpu_data = self.make_statistic_data(row=env_row + 2, column=3)

        # Network Status Labels
        self.make_statistic_label("WiFi Status:", row=net_row + 1, column=0)
        self.make_statistic_label("WLAN Status:", row=net_row + 2, column=0)
        self.make_statistic_label("   Local IP:", row=net_row + 1, column=2)
        self.make_statistic_label("    WLAN IP:", row=net_row + 2, column=2)

        # Network Status Data
        self.net_wifi_data = self.make_statistic_data(row=net_row + 1, column=1)
        self.net_internet_data = self.make_statistic_data(row=net_row + 2, column=1)
        self.net_lanip_data = self.make_statistic_data(row=net_row + 1, column=3)
        self.net_wanip_data = self.make_statistic_data(row=net_row + 2, column=3)

        # Device Status Labels
        self.make_statistic_label("   Outlet 1:", row=dev_row + 1, column=0)
        self.make_statistic_label("   Outlet 2:", row=dev_row + 2, column=0)
        self.make_statistic_label("   Outlet 3:", row=dev_row + 1, column=2)
        self.make_statistic_label("   Outlet 4:", row=dev_row + 2, column=2)
        self.make_statistic_label("       Door:", row=dev_row + 3, column=0)

        # Device Status Data
        self.dev_outlet_data = []
        self.dev_outlet_data.append(self.make_statistic_data(row=dev_row + 1, column=1))
        self.dev_outlet_data.append(self.make_statistic_data(row=dev_row + 2, column=1))
        self.dev_outlet_data.append(self.make_statistic_data(row=dev_row + 1, column=3))
        self.dev_outlet_data.append(self.make_statistic_data(row=dev_row + 2, column=3))
        self.dev_door_data = self.make_statistic_data(row=dev_row + 3, column=1)

    # Label Creator Methods
    def make_section_label(self, text, row):
        """Make the Section labels

        [extended_summary]

        Parameters
        ----------
        text : str
            The text for the section label
        row : int
            Which row of the GUI this label should be placed in

        Returns
        -------
        :obj:`tkinter.Label`
            The Label object
        """
        label = tk.Label(
            self.frame,
            font=("times", self.geom["FONTSIZE"], "bold"),
            bg=self.geom["STATBG"],
            fg="thistle2",
            text=text,
        )
        label.grid(row=row, columnspan=4)
        return label

    def make_statistic_label(self, text, row, column):
        """Make a label for a given statistic

        [extended_summary]

        Parameters
        ----------
        text : str
            The text for the statistic label
        row : int
            Which row of the GUI this label should be placed in
        column : int
            Which column of the GUI this label should be placed in

        Returns
        -------
        :obj:`tkinter.Label`
            The Label object
        """
        label = tk.Label(
            self.frame,
            font=("courier", self.geom["FONTSIZE"], "bold"),
            bg=self.geom["STATBG"],
            fg="lightgreen",
            text=text,
        )
        label.grid(row=row, column=column)
        return label

    def make_statistic_data(self, row, column):
        """Make the data object for a given statistic

        [extended_summary]

        Parameters
        ----------
        row : int
            Which row of the GUI this data should be placed in
        column : int
            Which column of the GUI this data should be placed in

        Returns
        -------
        :obj:`tkinter.Label`
            The Label object
        """
        label = tk.Label(
            self.frame,
            font=("courier", self.geom["FONTSIZE"], "bold"),
            bg=self.geom["STATBG"],
            fg="burlywood1",
            width=self.geom["DATAFIELD"],
        )
        label.grid(row=row, column=column)
        return label

    def close_window(self):
        """Close the window"""
        self.master.destroy()

    def update(self, now, sensors, relays, network):
        """Update the information in this Window

        [extended_summary]

        Parameters
        ----------
        now : :obj:`datetime.datetime`
            The current time at the update
        sensors : dict
            The dictionary containing the sensor objects
        relays : `chicken_devices.Relay`
            The Relay class
        """
        # Get the current time, and write
        self.display_time.config(text=now.strftime("%A, %B %-d, %Y    %-I:%M:%S %p"))

        # Set data update intervals
        short_interval = now.second % 15 == 0
        long_interval = now.second % 60 == 0

        # Write the various environment statuses at different intervals
        if short_interval:
            # File read
            self.env_cpu_data.config(text=self.format_cpu_str(sensors["cpu"].temp))
        if long_interval:
            # I2C Query
            self.env_inside_data.config(
                text=self.format_temp_humid_str(
                    sensors["inside"].temp, sensors["inside"].humid
                )
            )
            self.env_outside_data.config(
                text=self.format_temp_humid_str(
                    sensors["outside"].temp, sensors["outside"].humid
                )
            )
            self.env_pi_data.config(
                text=self.format_temp_humid_str(
                    sensors["box"].temp, sensors["box"].humid
                )
            )
            self.env_light_data.config(text=self.format_lux_str(sensors["light"].level))

        # Write the various device statuses at different intervals
        if short_interval:
            # Query class object
            for i, dev in enumerate(self.dev_outlet_data):
                dev.config(text="ENERGIZED" if relays.state[i] else "OFF")

        # Get the various network statuses & write
        if short_interval:
            network.update_lan()
            self.net_lanip_data.config(text=network.lan_ipv4)
            self.net_wifi_data.config(text=network.wifi_status)
        if long_interval:
            network.update_wan()
            self.net_internet_data.config(text=network.inet_status)
            self.net_wanip_data.config(text=network.wan_ipv4)

        # For short update interval, wait an additional 0.5 s before returning
        if short_interval:
            time.sleep(0.5)

    @staticmethod
    def format_temp_humid_str(temp, humid):
        """Format the Temperature/Humidity strings

        Parameters
        ----------
        temp : float
            The temperature to be displayed (ºF)
        humid : float
            The humidity to be displayed (%)

        Returns
        -------
        str
            The properly formatted string
        """
        return f"{temp:.1f}\xb0F, {humid:.1f}%"

    @staticmethod
    def format_lux_str(lux):
        """Formet the Lux strings

        Parameters
        ----------
        lux : float
            The light level to be displayed (lux)

        Returns
        -------
        str
            The properly formatted string
        """
        if lux is None:
            return "-" * 5
        if lux < 10:
            return f"{lux:.2f} lux"
        if lux < 100:
            return f"{lux:.1f} lux"
        return f"{lux:.0f} lux"

    @staticmethod
    def format_cpu_str(cputemp):
        """Format the CPU temperature string

        Parameters
        ----------
        cputemp : float
            The CPU temperature to be displayed (ºC)

        Returns
        -------
        str
            The properly formatted string
        """
        return (
            f"{cputemp:0.0f}\xb0F (<185\xb0F)"
            if cputemp is not None
            else "----- (<185\xb0F)"
        )
