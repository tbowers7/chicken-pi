# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import csv
import datetime
import logging

# 3rd Party Libraries
import astropy.table

# Internal Imports
from chicken import utils


class ChickenDatabase:
    """Database class for the Chicken-Pi

    This class manages all of the data collected and produced by the Chicken-Pi
    program.  It keeps the current day's values in memory, and writes it to
    disk at midnight.

    Data are stored in AstroPy Tables (inherited from the developer's
    professional background), and written to disk as FITS binary tables.  While
    other data management formats might be more universal, this form was deemed
    most expedient given the limited time available to the developer for
    writing this code.

    This class includes methods for recording data into the current table,
    writing tables to disk, and retrieving historical tables from disk.

    Parameters
    ----------
    logger : logging.Logger
        The logging object into which to place logs
    """

    def __init__(self, logger: logging.Logger):
        # Set up internal variables
        self.logger = logger
        now = datetime.datetime.now()

        # Check for existing FITS file for today -- read in or create new
        today_fn = utils.Paths.data.joinpath(f"coop_{now.strftime('%Y%m%d')}.fits")
        self.table = (
            astropy.table.Table.read(today_fn)
            if today_fn.exists()
            else astropy.table.Table()
        )

        # Log the startup time for the database
        self.logger.info(
            "Chicken-Pi database initialized: %s",
            now.isoformat(sep=" ", timespec="seconds"),
        )

    def add_row_to_table(self, nowobj, sensors, relays, network, debug=False):
        """Add a row of data to the table

        .. note::
            When adding a row to the Table, this method checks whether the
            date has changed.  If it has, then it writes the present Table to
            disk and starts a new (blank) Table for the new date.


        Parameters
        ----------
        nowobj : :obj:`datetime.datetime`
            The ``datetime`` object representing the official NOW
        sensors : [type]
            [description]
        relays : [type]
            [description]
        network : [type]
            [description]
        debug : bool, optional
            Print debugging statements?  (Default: False)
        """

        self.logger.debug("We're adding a row to the database at %s...", nowobj.time())

        # Begin populating the `row` dictionary with the date & time
        row = {"date": nowobj.strftime("%Y-%m-%d"), "time": nowobj.strftime("%H:%M:%S")}

        # Add the sensor readings to the row
        for name, sensor in sensors.items():
            # Retrieve the data from this sensor
            data = sensor.data_entry

            # If `data` is a tuple, it's a TH sensor, otherwise a LUX or CPU
            if isinstance(data, tuple):
                row[f"{name}_temp"] = data[0]
                row[f"{name}_humid"] = data[1]
            else:
                if name == "light":
                    row[f"{name}_lux"] = data
                elif name == "cpu":
                    row[f"{name}_temp"] = data

        # Add the relay status to the row
        for i, state in enumerate(relays.state, 1):
            row[f"outlet_{i}"] = state

        # Add network status to the row
        row["wifi_status"] = network.wifi_status
        row["inet_status"] = network.inet_status
        row["lan_ipv4"] = network.lan_ipv4
        row["wan_ipv4"] = network.wan_ipv4

        # Before appending the row to the end of the table, check new day
        #  If so, write out existing table and start a new one
        if "date" in self.table.colnames and row["date"] != self.table["date"][-1]:
            self.write_table_to_fits()
            self.table = astropy.table.Table()

        # Append the row to the end of the table
        self.table = astropy.table.vstack([self.table, row])
        if debug:
            self.table.pprint()

    def write_table_to_fits(self, date=None):
        """Write the table in memory to a FITS file on disk

        [extended_summary]

        Parameters
        ----------
        date : str, optional
            The YYMMDD string of the date to read in. [Default: None]
        """
        if date is None:
            dt_object = datetime.datetime.now() - datetime.timedelta(minutes=15)
            date = dt_object.strftime("%Y%m%d")
        self.logger.info(f"Writing the databse for {date} to disk...")
        self.table.write(utils.Paths.data.joinpath(f"coop_{date}.fits"), overwrite=True)

    def read_table_from_fits(self, date=None):
        """Read in a FITS file on disk

        _extended_summary_

        Parameters
        ----------
        date : _type_, optional
            _description_, by default None
        """

    def get_recent_weather(self, time_range=24):
        """get_recent_weather [summary]

        [extended_summary]

        Parameters
        ----------
        time_range : int, optional
            [description], by default 24
        """


# """
# Outline:
#     Daily make a new Table to hold observations
#     Record everything we want to every 5 mintues
#     At end of day (or at exit) write the Table to FITS in data/ directory

# Provide routines to:
#     Read in extant file for the day
#     Add lines to the table
#     Write out the Table to FITS
#     Retrieve information from the Table for graphing routines
# """


class OperationalSettings:
    """_summary_

    _extended_summary_
    """

    def __init__(self, outlets, door):

        # Set up internal variables
        self.file = utils.Paths.data.joinpath("operational_state.csv")

        # Read in state file, if exists
        if self.file.exists():
            self.read_settings(outlets, door)
        else:
            self.default_settings(outlets, door)

        # Internal Record of Settings
        self.settings = {}
        self.update_internal_record(outlets, door)

    def read_settings(self, outlets, door):
        """read_settings _summary_

        _extended_summary_

        Parameters
        ----------
        outlets : _type_
            _description_
        door : _type_
            _description_
        """
        # Read in the settings file
        with open(self.file, "r", encoding="utf-8") as statefile:
            state_reader = csv.reader(statefile, delimiter=",")

            # Should be 5 lines: one for each outlet, one for the door
            for i, states in enumerate(state_reader):

                if i < 4:
                    outlet = outlets[i]
                    # Read outlet states from file
                    # Enable CheckBox
                    if int(states[0]):
                        outlet.enable_box.select()
                    else:
                        outlet.enable_box.deselect()
                    outlet.update_enable()

                    # Time & Temp Sliders
                    outlet.on_slider.set(states[1])
                    outlet.update_on_time(states[1])

                    outlet.off_slider.set(states[2])
                    outlet.update_off_time(states[2])

                    outlet.temp_slider.set(states[5])
                    outlet.update_temp_trigger(states[5])

                    # Radio Buttons
                    outlet.andor_var.set(bool(int(states[3])))
                    outlet.update_andor()

                    outlet.tempsel_var.set(states[4])
                    outlet.update_temp_direction()
                else:
                    # Door
                    if int(states[0]):
                        door.door_enable.select()
                    else:
                        door.door_enable.deselect()
                    door.update_enable()

                    # Time & Temp Sliders
                    door.door_open_slider.set(states[1])
                    door.update_on_time(states[1])

                    door.door_closed_slider.set(states[2])
                    door.update_off_time(states[2])

                    door.door_light_slider.set(states[3])
                    door.update_door_light(states[3])

    @staticmethod
    def default_settings(outlets, door):
        """default_settings _summary_

        _extended_summary_

        Parameters
        ----------
        outlets : _type_
            _description_
        door : _type_
            _description_
        """
        for outlet in outlets:
            # Enable CheckBox -- Deselect
            outlet.enable_box.deselect()
            outlet.update_enable()
            # Time & Temp Sliders -- Times to Noon, Temp to 50º
            outlet.on_slider.set(12)
            outlet.update_on_time(12)
            outlet.off_slider.set(12)
            outlet.update_off_time(12)
            outlet.temp_slider.set(50)
            outlet.update_temp_trigger(50)
            # Radio Buttons
            outlet.andor_var.set(False)
            outlet.update_andor()
            outlet.tempsel_var.set(0)
            outlet.update_temp_direction()
        # Door
        door.door_enable.deselect()
        door.update_enable()
        # Time & Temp Sliders
        door.door_open_slider.set(12)
        door.update_on_time(12)
        door.door_closed_slider.set(12)
        door.update_off_time(12)
        door.door_light_slider.set(2.65)
        door.update_door_light(2.65)

    def write_settings(self, outlets, door):
        """write_settings _summary_

        _extended_summary_

        Parameters
        ----------
        outlets : _type_
            _description_
        door : _type_
            _description_
        """
        # Create a list of the operational settings
        # Go through the GUI, outlet by outlet -- top to bottom -- then door
        with open(self.file, "w", encoding="utf-8") as statefile:
            state_writer = csv.writer(statefile, delimiter=",")

            # Write each outlet and door as a separate line
            for outlet in outlets:
                settings = []
                settings.append(int(outlet.enable))
                settings.append(outlet.on_time)
                settings.append(outlet.off_time)
                settings.append(int(outlet.and_or))
                settings.append(outlet.temp_direction)
                settings.append(outlet.switch_temp)
                state_writer.writerow(settings)

            settings = []
            settings.append(int(door.enable))
            settings.append(door.on_time)
            settings.append(door.off_time)
            settings.append(door.switch_temp)
            state_writer.writerow(settings)

    def check_for_change(self, outlets, door):
        """check_for_change _summary_

        _extended_summary_

        Parameters
        ----------
        outlets : _type_
            _description_
        door : _type_
            _description_
        """
        # Check the outlets against saved values
        test = []
        for i, outlet in enumerate(outlets, 1):
            test.append(self.settings[f"outlet_{i}"]["enable"] == outlet.enable)
            test.append(self.settings[f"outlet_{i}"]["on_time"] == outlet.on_time)
            test.append(self.settings[f"outlet_{i}"]["off_time"] == outlet.off_time)
            test.append(self.settings[f"outlet_{i}"]["and_or"] == outlet.and_or)
            test.append(
                self.settings[f"outlet_{i}"]["temp_direction"] == outlet.temp_direction
            )
            test.append(
                self.settings[f"outlet_{i}"]["switch_temp"] == outlet.switch_temp
            )
        test.append(self.settings["door"]["enable"] == door.enable)
        test.append(self.settings["door"]["on_time"] == door.on_time)
        test.append(self.settings["door"]["off_time"] == door.off_time)
        test.append(self.settings["door"]["switch_temp"] == door.switch_temp)

        if not all(test):
            # print("Something changed!!!!")
            self.update_internal_record(outlets, door)
            self.write_settings(outlets, door)

    def update_internal_record(self, outlets, door):
        """update_internal_record _summary_

        _extended_summary_

        Parameters
        ----------
        outlets : _type_
            _description_
        door : _type_
            _description_
        """
        for i, outlet in enumerate(outlets, 1):
            self.settings[f"outlet_{i}"] = {
                "enable": outlet.enable,
                "on_time": outlet.on_time,
                "off_time": outlet.off_time,
                "and_or": outlet.and_or,
                "temp_direction": outlet.temp_direction,
                "switch_temp": outlet.switch_temp,
            }
        self.settings["door"] = {
            "enable": door.enable,
            "on_time": door.on_time,
            "off_time": door.off_time,
            "switch_temp": door.switch_temp,
        }
