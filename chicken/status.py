# -*- coding: utf-8 -*-

"""
  FILE: chicken_status.py

Status display window, updates frequently with current values

"""

# Built-In Libraries
from tkinter import Frame, Label
import time
import os

# 3rd Party Libraries
from requests import get
from requests import exceptions as rexcept
import urllib3
from urllib3.exceptions import NewConnectionError, ConnectTimeoutError

# Internal Imports
try:
    from chicken.device import Relay
    relay = Relay()   # Instantiate class
except ModuleNotFoundError:
    pass

# Geometry
PI_TOOLBAR = 36
TK_HEADER  = 25

# Constants
WIDGET_WIDE  = 600           # Width of the "Status Window"
WIDGET_HIGH  = 300           # Height of the "Status Window"
STATBG       = 'black'
FONTSIZE     = 13
DATAFIELD    = 15
ENVROW       = 1
DEVROW       = 5
NETROW       = 9

# Enable testing on both Raspberry Pi and Mac
if os.path.exists("/usr/bin/uname"):
    _UNAME = "/usr/bin/uname"
elif os.path.exists("/bin/uname"):
    _UNAME = "/bin/uname"
else:
    _UNAME = ""
SYSTYPE = (os.popen(f"{_UNAME} -a").read()).split()[0]
WLAN = 'en0' if SYSTYPE == 'Darwin' else 'wlan0'


class StatusWindow():
    """
    StatusWindow class
    Creates the status window and (supposedly) updates it from time to time.
    """
    def __init__(self, master, CONTROL_WIDTH):
        """
        __init__ method: initializes the Status Window
        """
        # Define the MASTER for the window, set geometry
        self.master = master
        self.master.geometry(
            f"{WIDGET_WIDE}x{WIDGET_HIGH}+{CONTROL_WIDTH+10}+{PI_TOOLBAR}")
        self.master.title("Status Window")
        self.master.configure(bg=STATBG)

        # A "frame" holds the various window contents
        self.frame = Frame(self.master, bg=STATBG)
        self.frame.pack(expand=0)

        # Put the time at the top of the window
        self.display_time = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                              bg=STATBG, fg='skyblue')
        self.display_time.grid(row=0, columnspan=4)

        # Create the various section labels
        self.make_section_label('Environmental Status', row=ENVROW)
        self.make_section_label('Network Status', row=NETROW)
        self.make_section_label('Device Status', row=DEVROW)

        # Environmental Status Labels
        self.make_statistic_label('    Outside:', row=ENVROW+1, column=0)
        self.make_statistic_label('Inside Coop:', row=ENVROW+2, column=0)
        self.make_statistic_label('Light Level:', row=ENVROW+3, column=0)
        self.make_statistic_label(' Inside Box:', row=ENVROW+1, column=2)
        self.make_statistic_label('   RPi4 CPU:', row=ENVROW+2, column=2)

        # Environmental Status Data
        self.env_outside_data = self.make_statistic_data(row=ENVROW+1, column=1)
        self.env_inside_data = self.make_statistic_data(row=ENVROW+2, column=1)
        self.env_light_data = self.make_statistic_data(row=ENVROW+3, column=1)
        self.env_pi_data = self.make_statistic_data(row=ENVROW+1, column=3)
        self.env_cpu_data = self.make_statistic_data(row=ENVROW+2, column=3)

        # Network Status Labels
        self.make_statistic_label('WiFi Status:', row=NETROW+1, column=0)
        self.make_statistic_label('WLAN Status:', row=NETROW+2, column=0)
        self.make_statistic_label('   Local IP:', row=NETROW+1, column=2)
        self.make_statistic_label('    WLAN IP:', row=NETROW+2, column=2)

        # Network Status Data
        self.net_wifi_data = self.make_statistic_data(row=NETROW+1, column=1)
        self.new_internet_data = self.make_statistic_data(row=NETROW+2, column=1)
        self.net_lanip_data = self.make_statistic_data(row=NETROW+1, column=3)
        self.net_wanip_data = self.make_statistic_data(row=NETROW+2, column=3)

        # Device Status Labels
        self.make_statistic_label('   Outlet 1:', row=DEVROW+1, column=0)
        self.make_statistic_label('   Outlet 2:', row=DEVROW+2, column=0)
        self.make_statistic_label('   Outlet 3:', row=DEVROW+1, column=2)
        self.make_statistic_label('   Outlet 4:', row=DEVROW+2, column=2)
        self.make_statistic_label('       Door:', row=DEVROW+3, column=0)

        # Device Status Data
        self.dev_outlet_data = []
        self.dev_outlet_data.append(self.make_statistic_data(row=DEVROW+1, column=1))
        self.dev_outlet_data.append(self.make_statistic_data(row=DEVROW+2, column=1))
        self.dev_outlet_data.append(self.make_statistic_data(row=DEVROW+1, column=3))
        self.dev_outlet_data.append(self.make_statistic_data(row=DEVROW+2, column=3))
        self.dev_door_data = self.make_statistic_data(row=DEVROW+3, column=1)

    # Label Creator Methods
    def make_section_label(self, text, row):
        """make_section_label Make the Section labels

        [extended_summary]

        Parameters
        ----------
        text : `str`
            The text for the section label
        row : `int`
            Which row of the GUI this label should be placed in

        Returns
        -------
        `tkinter.Label`
            The Label object
        """
        label = Label(self.frame, font=('times', FONTSIZE, 'bold'),
                      bg=STATBG, fg='thistle2', text=text)
        label.grid(row=row, columnspan=4)
        return label

    def make_statistic_label(self, text, row, column):
        """make_statistic_label Make a label for a given statistic

        [extended_summary]

        Parameters
        ----------
        text : `str`
            The text for the statistic label
        row : `int`
            Which row of the GUI this label should be placed in
        column : `int`
            Which column of the GUI this label should be placed in

        Returns
        -------
        `tkinter.Label`
            The Label object
        """
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='lightgreen', text=text)
        label.grid(row=row, column=column)
        return label

    def make_statistic_data(self, row, column):
        """make_statistic_data Make the data object for a given statistic

        [extended_summary]

        Parameters
        ----------
        row : `int`
            Which row of the GUI this data should be placed in
        column : `int`
            Which column of the GUI this data should be placed in

        Returns
        -------
        `tkinter.Label`
            The Label object
        """
        label = Label(self.frame, font=('courier', FONTSIZE, 'bold'),
                      bg=STATBG, fg='burlywood1', width=DATAFIELD)
        label.grid(row=row, column=column)
        return label

    def close_window(self):
        """close_window Close the window
        """
        self.master.destroy()

    def update(self, now, sensors, relays):
        """update Update the information in this Window

        [extended_summary]

        Parameters
        ----------
        now : `datetime.datetime`
            The current time at the update
        sensors : `dict`
            The dictionary containing the sensor objects
        relays : `chicken_devices.Relay`
            The Relay class
        """
        # Get the current time, and write
        self.display_time.config(text =
            now.strftime("%A, %B %-d, %Y    %-I:%M:%S %p"))

        # Set data update intervals
        short_interval = now.second % 15 == 0
        long_interval = now.second % 60 == 0

        # Write the various environment statuses at different intervals
        if short_interval:
            self.env_cpu_data.config(text = format_cpu_str(get_cpu_temp()))
        if long_interval:
            self.env_inside_data.config(text =
                format_temp_humid_str(sensors['inside'].temp, sensors['inside'].humid))
            self.env_outside_data.config(text =
                format_temp_humid_str(sensors['outside'].temp, sensors['outside'].humid))
            self.env_pi_data.config(text =
                format_temp_humid_str(sensors['box'].temp, sensors['box'].humid))
            self.env_light_data.config(text =
                format_lux_str(sensors['light'].level))

        # Write the various device statuses at different intervals
        if short_interval:
            for i, dev in enumerate(self.dev_outlet_data):
                dev.config(text = 'ENERGIZED' if relays.state[i] else 'OFF')

        # Write the various network statuses
        if short_interval:
            self.net_lanip_data.config(text = get_local_ipv4())
            self.net_wifi_data.config(text =
                'ON' if contact_server('192.168.0.1') else 'OFF')
        if long_interval:
            self.new_internet_data.config(text =
                'ON' if contact_server('1.1.1.1') else 'OFF')
            self.net_wanip_data.config(text = get_public_ipv4())

        # For short update interval, wait an additional 0.5 s before returning
        if short_interval:
            time.sleep(0.5)


# Network Checking Functions =======================================#
def contact_server(host='192.168.0.1'):
    """contact_server Check whether a server is reachable

    [extended_summary]

    Parameters
    ----------
    host : `str`, optional
        Name or IP address of server to contact [Default: '192.168.0.1']

    Returns
    -------
    `bool`
        Whether server is reachable
    """
    try:
        http = urllib3.PoolManager()
        http.request('GET', host, timeout=3, retries=False)
        return True
    except (NewConnectionError, ConnectTimeoutError):
        return False


def get_local_ipv4():
    """get_local_IP Return the local (LAN) IP address for the Pi

    Use `ifconfig` to read the local IP address assigned to the Pi by the
    local DHCP server.

    Returns
    -------
    `str`
        LAN IP address
    """
    cmd = f"/sbin/ifconfig {WLAN} | grep 'inet ' | awk '{{print $2}}'"
    return (os.popen(cmd).read()).strip()


def get_public_ipv4():
    """get_public_IP Return the public-facing IP address for the Pi

    Query ipify.org to return the public (WAN) IP address for the network
    appliance to which the Chicken-Pi is attached.

    If an error message is kicked by ipify.org, then the response will be
    longer than the maximum 15 characters (xxx.xxx.xxx.xxx).  In this case,
    the function will return '-----' rather than an IP address.

    Returns
    -------
    `str`
        Public IP address
    """
    try:
        public_ipv4 = (get('https://api.ipify.org', timeout=10).text).strip()
        # If response is longer than the maximum 15 characters, return '---'.
        if len(public_ipv4) > 15:
            public_ipv4 = '-----'
    except (rexcept.ConnectionError, ConnectionError):
        public_ipv4 = '-----'
    return public_ipv4


# Environmental Checking Functions
def get_cpu_temp():
    """get_cpu_temp Read the CPU temperature from system file

    [extended_summary]

    Returns
    -------
    `float`
        CPU temperature in ºF
    """
    # Check Pi CPU Temp:
    if SYSTYPE == 'Linux':
        cputemp_fn = "/sys/class/thermal/thermal_zone0/temp"
        with open(cputemp_fn,"r") as sys_file:
            return (float(sys_file.read()) /1000.) * 9./5. + 32.
    return None


# Status Checking Functions
def get_outlet_status():
    """get_outlet_status Get the status of the outlets

    [extended_summary]

    Returns
    -------
    `list` of `bool`
        A list of the True/False states for the 4 relays.
    """
    try:
        # Read the relay_status
        return relay.status()
    except ValueError:
        return [False] * 4


# String Formatting Functions
def format_temp_humid_str(temp, humid):
    """format_temp_humid_str Format the Temperature/Humidity strings

    Parameters
    ----------
    temp : `float`
        The temperature to be displayed (ºF)
    humid : `float`
        The humidity to be displayed (%)

    Returns
    -------
    `str`
        The properly formatted string
    """
    return f"{temp:.1f}\xb0F, {humid:.1f}%"


def format_lux_str(lux):
    """format_lux_str Formet the Lux strings

    Parameters
    ----------
    lux : `float`
        The light level to be displayed (lux)

    Returns
    -------
    `str`
        The properly formatted string
    """
    if lux is None:
        return '-'*5
    if lux < 10:
        return f"{lux:.2f} lux"
    if lux < 100:
        return f"{lux:.1f} lux"
    return f"{lux:.0f} lux"


def format_cpu_str(cputemp):
    """format_cpu_str Format the CPU temperature string

    Parameters
    ----------
    cputemp : `float`
        The CPU temperature to be displayed (ºC)

    Returns
    -------
    `str`
        The properly formatted string
    """
    return f"{cputemp:0.0f}\xb0F (<185\xb0F)" if cputemp is not None \
        else "----- (<185\xb0F)"
