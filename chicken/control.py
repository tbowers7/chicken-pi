# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: control.py

Control window, with all the shiny knobs and buttons

"""

# Built-In Libraries
import datetime
from tkinter import Toplevel, Frame, Label, Checkbutton, Scale, Radiobutton, \
    PhotoImage, BooleanVar, IntVar, DoubleVar, \
    BOTH, W, E, HORIZONTAL, LEFT, DISABLED

# 3rd Party Libraries
import numpy as np

# Internal Imports
from chicken.database import ChickenDatabase, OperationalSettings
from chicken.graphs import GraphsWindow
from chicken.network import NetworkStatus
from chicken.status import StatusWindow
try:
    from chicken.device import set_up_sensors, Relay
except ModuleNotFoundError:
    from chicken.dummy import set_up_sensors, Relay

# Geometry
PI_TOOLBAR = 36
TK_HEADER  = 25

# Constants
OUT1STR      = "Roost Lamp"  # Name of what is plugged into outlet #1
OUT2STR      = "Red Light "  # Name of what is plugged into outlet #2
OUT3STR      = "Nest Lamp "  # Name of what is plugged into outlet #3
OUT4STR      = "__________"  # Name of what is plugged into outlet #4
WIDGET_WIDE  = 600           # Width of the "Control Window"
WIDGET_HIGH  = 400           # Height of the "Control Window"
OUTROW       = 2
DOORROW      = OUTROW + 14
CONTBG       = 'lightgreen'


class ControlWindow():
    """
    ControlWindow class
    Creates the main control window and also spawns the secondary display
    windows.
    """
    def __init__(self, master, base_dir):
        """
        __init__: initializes the class, including geometry and spawning
        display windows
        """
        self.use_nws = False
        self.sensors = set_up_sensors()
        self.relays = Relay()
        self.network = NetworkStatus()
        self.led_loc = f"{base_dir}/resources"

        # Set up the database
        self.data = ChickenDatabase(base_dir)

        # Define the MASTER for the window, and spawn the other two windows
        self.master = master
        self.status_window = StatusWindow(Toplevel(self.master), WIDGET_WIDE)
        if self.use_nws:
            self.graphs_window = GraphsWindow(Toplevel(self.master,
                                                       bg='forestgreen'))

        # Define the geometry and title for the control window
        self.master.geometry(f"{WIDGET_WIDE}x{WIDGET_HIGH}+0+{PI_TOOLBAR}")
        self.master.title("Control Window")
        self.master.configure(bg=CONTBG)

        ## A "frame" holds the various GUI controls
        self.frame = Frame(self.master)
        self.frame.pack(expand=1, fill=BOTH)

        #===== SWITCHED OUTLETS =====#
        Label(self.frame, text='Relay-Controlled Outlets', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=OUTROW-1, column=0, columnspan=4, sticky=W+E)

        self.outlet = []
        for i, name in enumerate([OUT1STR, OUT2STR, OUT3STR, OUT4STR]):
            self.outlet.append(OutletControl(self.frame, name, i,
                                             self.sensors, self.led_loc))

        #===== DOOR =====#
        Label(self.frame, text=' - '*40,fg='darkblue').grid(
            row=DOORROW-1, column=0, columnspan=4, sticky=W+E)
        Label(self.frame, text='Automated Chicken Door', fg='darkblue',
              bg='#ffff80', font=('courier', 14, 'bold')).grid(
                  row=DOORROW, column=0, columnspan=4, sticky=W+E)

        self.door = DoorControl(self.frame, self.sensors)

        # Set up the 'SaveSettings' object
        self.settings = OperationalSettings(base_dir, self.outlet, self.door)

    def set_relays(self, change=False):
        """set_relays Write the relay commands to the Relay HAT

        [extended_summary]
        """
        # Check to see if any states have changed
        for i,outlet in enumerate(self.outlet):
            demand = outlet.demand     # Call just once, since this queries I2C
            if self.relays.state[i] != demand:
                self.relays.state[i] = demand
                change = True

        # If so, write
        if change:
            self.relays.write()

    # Update Method #
    def update(self):
        """update Update the display windows

        [extended_summary]
        """
        # This is the official time for Chicken Pi
        now = datetime.datetime.now()

        # Check for changed in the GUI settings
        self.settings.check_for_change(self.outlet, self.door)

        # Every 60 seconds, write changes in relay command to relays
        if now.second % 60 == 0:
            self.set_relays()

        # Update status window on 0.5s cadence
        self.status_window.update(now, self.sensors, self.relays, self.network)

        # Update the NWS Graph window, if enableed
        if self.use_nws:
            self.graphs_window.update(now)

        # Update the command tags in the Control Window
        for outlet in self.outlet:
            outlet.img = PhotoImage(file=
                f"{self.led_loc}/green-led-on-th.png" if outlet.state else \
                f"{self.led_loc}/green-led-off-th.png")
            outlet.command_led.configure(image=outlet.img)

        # Every 5 minutes, write status to database
        if now.second % 60 == 0 and now.minute % 5 == 0:
            self.write_to_database(now)

        # Wait 0.5 seconds and repeat
        self.master.after(500, self.update)

    def write_to_database(self, now):
        """write_to_database Write the current readings to the database

        [extended_summary]

        Parameters
        ----------
        now : `datetime.datetime`
            The current time object, for including in the database
        """
        print("Writing readings to the database...")
        self.data.add_row_to_table(now, self.sensors, self.relays, self.network)

    def write_database_to_disk(self):
        """write_database_to_disk Write the entire database to disk

        [extended_summary]
        """
        self.write_to_database(datetime.datetime.now())
        print("Writing the databse to disk...")
        self.data.write_table_to_fits()


class _BaseControl():
    """Base class for Object Control

    """

    def __init__(self):
        """Initialize Class

        """
        ## Initialize the various variables required
        self.enable  = False         # Switch Enabled
        self.and_or   = False        # Time AND/OR Temperature
        self.on_time  = 0            # Switch turn on time
        self.off_time = 0            # Switch turn off time
        self.switch_temp = 20        # Temp / Light trigger for switch
        self.temp_direction = 0      # Temperature direction for trigger
        self.en_var = BooleanVar()   # Variable needed for ENABLE boxes
        self.tempsel_var = IntVar()  # Variable needed for temp radio button
        self.andor_var = BooleanVar() # Variable needed for the ... ?
        self.time_cycle = 0          # Time cycle: ON or ON-OFF-ON or OFF-ON-OFF
        self.on_label = None         # Dummy -- To be created by inheriting class
        self.off_label = None        # Dummy -- To be created by inheriting class

    # Various Update Methods
    def update_enable(self):
        """update_enable Update the ENABLE state for this device

        [extended_summary]
        """
        self.enable = self.en_var.get()

    def update_on_time(self, seltime):
        """update_on_time Update the turn-on time for this device

        [extended_summary]

        Parameters
        ----------
        seltime : `string` or `float`
            The selected time from the Tk widget
        """
        self.on_time = float(seltime)
        self.on_label.config(text=f" ON {string_time(self.on_time)}")
        self.update_time_cycle()

    def update_off_time(self, seltime):
        """update_off_time Update the turn-off time for this device

        [extended_summary]

        Parameters
        ----------
        seltime : `string` or `float`
            The selected time from the Tk widget
        """
        self.off_time = float(seltime)
        self.off_label.config(text=f" OFF {string_time(self.off_time)}")
        self.update_time_cycle()

    def update_time_cycle(self):
        """update_time_cycle Update the time cycle for this device

        [extended_summary]
        """
        if self.on_time == self.off_time or abs(self.on_time - self.off_time) == 24:
            self.time_cycle = 0                    # ON always
        elif self.on_time > self.off_time:
            self.time_cycle = 1                    # ON - OFF - ON
        else:
            self.time_cycle = 2                    # OFF - ON - OFF


class OutletControl(_BaseControl):
    """Outlet Control Class

    """

    def __init__(self, frame, name, column, sensors, led_loc):
        """Initialize Class

        Inputs:
          frame:
          name:
          column:
        """
        _BaseControl.__init__(self)
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window

        # Init variable
        self.sensors = sensors

        # Column Label for this outlet
        Label(frame, text=f"{name} (#{column+1})",
            bg='#f0f0f0').grid(row=OUTROW+1, column=column, sticky=W+E)

        # Individual Labels:
        self.on_label = Label(frame, fg='green', bg='#e0ffe0',
                              text=f" ON {string_time(self.on_time)}")
        self.off_label = Label(frame, fg='red', bg='#ffe0e0',
                               text=f" OFF {string_time(self.off_time)}")
        self.temp_label = Label(frame, fg='blue', bg='#e0e0ff',
                                text=f" Coop Temp {string_temp(self.switch_temp)}")

        # Enable Box
        self.enable_box = Checkbutton(frame, text='Enable', variable=self.en_var,
                                      command=self.update_enable, onvalue=True,
                                      offvalue=False)

        # Sliders
        self.on_slider = Scale(frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                               resolution=0.25, command=self.update_on_time,
                               variable=DoubleVar, length=slider_size, showvalue=0,
                               troughcolor='#bfd9bf')
        self.off_slider = Scale(frame, from_=0, to=24, digits=4, orient=HORIZONTAL,
                                resolution=0.25, command=self.update_off_time,
                                variable=DoubleVar, length=slider_size, showvalue=0,
                                troughcolor='#d9bfbf')
        self.temp_slider = Scale(frame, from_=20, to=80, digits=2, orient=HORIZONTAL,
                                 resolution=5, command=self.update_temp_trigger,
                                 variable=IntVar, length=slider_size, showvalue=0,
                                 troughcolor='#bfbfd9')

        # AND/OR Buttons
        self.and_or_frame = Frame(frame)
        self.and_button = Radiobutton(self.and_or_frame, indicatoron=0, value=True,
                                      text='   AND   ', variable=self.andor_var,
                                      command=self.update_andor, bg='#e0e0e0',
                                      selectcolor='#50C878')
        self.or_button = Radiobutton(self.and_or_frame, indicatoron=0, value=False,
                                     text='   OR   ', variable=self.andor_var,
                                     command=self.update_andor, bg='#e0e0e0',
                                     selectcolor='#50C878')

        # Temperature Direction Radio Buttons
        self.no_temp_button = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=0,
                                          command=self.update_temp_direction,
                                          variable=self.tempsel_var, anchor=W,
                                          text='Temp independent', font=('',9))
        self.up_temp_button = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=1,
                                          command=self.update_temp_direction,
                                          variable=self.tempsel_var, anchor=W,
                                          text='Turn ON above: ')
        self.down_temp_button = Radiobutton(frame, fg='blue', bg='#f0f0ff', value=-1,
                                            command=self.update_temp_direction,
                                            variable=self.tempsel_var, anchor=W,
                                            text='Turn ON below:')

        self.img = PhotoImage(file=f"{led_loc}/green-led-off-th.png")
        self.command_led = Label(frame, image=self.img)

        # Set everything to the grid
        self.on_label.grid(row=OUTROW+3, column=column, sticky=W+E)
        self.off_label.grid(row=OUTROW+5, column=column, sticky=W+E)
        self.temp_label.grid(row=OUTROW+11, column=column, sticky=W+E)
        self.enable_box.grid(row=OUTROW+2, column=column)
        self.on_slider.grid(row=OUTROW+4, column=column, sticky=W+E)
        self.off_slider.grid(row=OUTROW+6, column=column, sticky=W+E)
        self.temp_slider.grid(row=OUTROW+12, column=column, sticky=W+E)
        self.and_or_frame.grid(row=OUTROW+7, column=column, sticky=W+E)
        self.and_button.pack(side=LEFT, expand=1)
        self.or_button.pack(side=LEFT, expand=1)
        self.no_temp_button.grid(row=OUTROW+8, column=column, sticky=W+E)
        self.up_temp_button.grid(row=OUTROW+9, column=column, sticky=W+E)
        self.down_temp_button.grid(row=OUTROW+10, column=column, sticky=W+E)
        self.command_led.grid(row=OUTROW, column=column, sticky=W+E)

    def update_temp_trigger(self,seltemp):
        """update_temp_trigger Update the temperature trigger point

        [extended_summary]

        Parameters
        ----------
        seltemp : `float`
            Selected temperature from the Tk widget
        """
        self.switch_temp = int(seltemp)
        self.temp_label.config(text=f" Coop Temp {string_temp(self.switch_temp)}")

    def update_andor(self):
        """update_andor Update the AND/OR flag for tempature/time

        [extended_summary]
        """
        self.and_or = self.andor_var.get()

    def update_temp_direction(self):
        """update_temp_direction Update the temperature trigger direction

        [extended_summary]
        """
        self.temp_direction = self.tempsel_var.get()

    def cmd_state(self, nowobj, use_cache=False):
        """cmd_state Construct the commanded state from the control knobs

        [extended_summary]

        Parameters
        ----------
        nowobj : `datetime.datetime`
            The output of `datetime.datetime.now()`
        use_cache : `bool`, optional
            Use the cached sensor values rather thsn checking? [Default: False]

        Returns
        -------
        `bool`
            Should the device be on or off?
        """
        # If 'ENABLE' box not checked, keep off
        if not self.enable:
            return False

        # Get time commanded state
        nowh = nowobj.hour + nowobj.minute/60. + nowobj.second/3600.
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
        intemp = self.sensors['inside'].temp if not use_cache else \
            self.sensors['inside'].cache_temp
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
        """demand Return the demanded state as a class attribute

        Returns
        -------
        `bool`
            The current demanded state of the device
        """
        return self.cmd_state(datetime.datetime.now())

    @property
    def state(self):
        """state Returned the cached state as a class attribute

        Returns
        -------
        `bool`
            The current (cached) state of the device
        """
        return self.cmd_state(datetime.datetime.now(), use_cache=True)


class DoorControl(_BaseControl):
    """Door Control Class

    """

    def __init__(self, frame, sensors):
        """Initialize Class

        Inputs:
          frame:
        """
        _BaseControl.__init__(self)
        slider_size = (WIDGET_WIDE - 5*5) / 4   # Scale slider width to window

        # Init variable
        self.sensors = sensors

        # Column 0: ENABLE
        self.door_enable = Checkbutton(frame, text='Enable', onvalue=True,
                                       offvalue=False, variable=self.en_var,
                                       command=self.update_enable, state=DISABLED)

        # Column 1: Open Time
        self.on_label = Label(frame, fg='green', bg='#e0ffe0',
                              text=f" OPEN {string_time(self.on_time)}")
        self.door_open_slider = Scale(frame, from_=0, to=24, digits=4,
                                      orient=HORIZONTAL, resolution=0.25,
                                      command=self.update_on_time, showvalue=0,
                                      variable=DoubleVar, length=slider_size,
                                      troughcolor='#bfd9bf')

        # Column 2: Close Time
        self.off_label = Label(frame, fg='red', bg='#ffe0e0',
                               text=f" CLOSE {string_time(self.off_time)}")
        self.door_closed_slider = Scale(frame, from_=0, to=24, digits=4,
                                       orient=HORIZONTAL, resolution=0.25,
                                       command=self.update_off_time,showvalue=0,
                                       variable=DoubleVar, length=slider_size,
                                       troughcolor='#d9bfbf')

        # Column 3: Light Trigger
        self.switch_temp = 2
        self.door_light_label = Label(frame, fg='#9932cc', bg='#f3e6f9',
                                    text=f" LIGHT {string_light(self.switch_temp)}")
        self.door_light_slider = Scale(frame, from_=2, to=4, digits=4,
                                     orient=HORIZONTAL, resolution=0.05,
                                     command=self.update_door_light,showvalue=0,
                                     variable=DoubleVar, length=slider_size,
                                     troughcolor='#cfc4d4')

        # Set everything to the grid
        self.door_enable.grid(row=DOORROW+1, column=0, rowspan=2)
        self.on_label.grid(row=DOORROW+1, column=1, sticky=W+E)
        self.door_open_slider.grid(row=DOORROW+2, column=1, sticky=W+E)
        self.off_label.grid(row=DOORROW+1, column=2, sticky=W+E)
        self.door_closed_slider.grid(row=DOORROW+2, column=2, sticky=W+E)
        self.door_light_label.grid(row=DOORROW+1, column=3, sticky=W+E)
        self.door_light_slider.grid(row=DOORROW+2, column=3, sticky=W+E)

    # Light Update Method
    def update_door_light(self, sellux):
        """update_door_light Update the door light trigger

        [extended_summary]

        Parameters
        ----------
        sellux : `float`
            Selected lux from the Tk widget
        """
        self.switch_temp = float(sellux)
        self.door_light_label.config(text=f" LIGHT {string_light(self.switch_temp)}")


# String Formatting Functions ======================================#
def string_time(in_time):
    """string_time Create a printable string for the slider bar

    [extended_summary]

    Parameters
    ----------
    in_time : `float`
        Input time from the Tk widget

    Returns
    -------
    `str`
        The formatted string
    """
    hour, minute = (int(in_time), 60 * (in_time % 1)) # Compute minutes from in_time
    hour = 0 if hour == 24 else hour                # Catch case of 24:00
    ampm = "PM" if hour >= 12 else "AM"             # Set PM/AM times
    if hour >= 12:
        hour -= 12
    hour = 12 if hour == 0 else hour                # Catch case of 0:00
    return f"{hour:2d}:{int(minute):0>2d} {ampm}"


def string_temp(in_temperature):
    """string_temp Create a printable string for the slider bar

    [extended_summary]

    Parameters
    ----------
    in_temperature : `float`
        Input temperature from the Tk widget

    Returns
    -------
    `str`
        The formatted string
    """
    return f"{int(in_temperature):2d}\N{DEGREE SIGN} F"


def string_light(in_log_lux):
    """string_light Create a printable string for the slider bar

    [extended_summary]

    Parameters
    ----------
    in_log_lux : `float`
        Input log lux from the Tk widget

    Returns
    -------
    `str`
        The formatted string
    """
    display_lux = 10 ** in_log_lux
    # Round to make look pretty
    display_lux = np.round(display_lux / 10.) * 10. if display_lux < 1000 else \
        np.round(display_lux / 100.) * 100.
    return f"{display_lux:,.0f} lux"
