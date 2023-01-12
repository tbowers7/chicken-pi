# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import csv
import datetime
from os.path import exists

# 3rd Party Libraries
from astropy.table import Table, vstack

# Internal Imports


class ChickenDatabase:
    """ChickenDatabase Database class for the Chicken-Pi

    [extended_summary]
    """

    def __init__(self, base_dir):
        # Set up internal variables
        self.base_dir = base_dir

        now = datetime.datetime.now()
        self.date = now
        print(f"Chicken-Pi database initialized: {now.date()} {now.time()}")

        # Check for existing FITS file for today -- read in or create new
        today_fn = f"{self.base_dir}/data/coop_{now.strftime('%Y%m%d')}.fits"
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
        date = datetime.datetime.now().strftime("%Y%m%d") if date is None else date
        return Table.read(f"{self.base_dir}/data/coop_{date}.fits")

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
        row["date"] = nowobj.strftime("%Y-%m-%d")
        row["time"] = nowobj.strftime("%H:%M:%S")

        # Add the sensor readings to the row
        for name in sensors.keys():
            # Retrieve the data from this sensor
            data = sensors[name].data_entry

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
            date = dt_object.strftime("%Y%m%d")
        self.table.write(f"{self.base_dir}/data/coop_{date}.fits", overwrite=True)

    def get_recent_weather(self, time_range=24):
        """get_recent_weather [summary]

        [extended_summary]

        Parameters
        ----------
        time_range : int, optional
            [description], by default 24
        """


"""
Outline:
    Daily make a new Table to hold observations
    Record everything we want to every 5 mintues
    At end of day (or at exit) write the Table to FITS in data/ directory

Provide routines to:
    Read in extant file for the day
    Add lines to the table
    Write out the Table to FITS
    Retrieve information from the Table for graphing routines
"""


class OperationalSettings:
    """_summary_

    _extended_summary_
    """

    def __init__(self, base_dir, outlets, door):

        # Set up internal variables
        self.file = f"{base_dir}/data/operational_state.csv"

        # Read in state file, if exists
        if exists(self.file):
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
        with open(self.file, "w", encoding='utf-8') as statefile:
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
        tt = []
        for i, outlet in enumerate(outlets, 1):
            tt.append(self.settings[f"outlet_{i}"]["enable"] == outlet.enable)
            tt.append(self.settings[f"outlet_{i}"]["on_time"] == outlet.on_time)
            tt.append(self.settings[f"outlet_{i}"]["off_time"] == outlet.off_time)
            tt.append(self.settings[f"outlet_{i}"]["and_or"] == outlet.and_or)
            tt.append(
                self.settings[f"outlet_{i}"]["temp_direction"] == outlet.temp_direction
            )
            tt.append(self.settings[f"outlet_{i}"]["switch_temp"] == outlet.switch_temp)
        tt.append(self.settings["door"]["enable"] == door.enable)
        tt.append(self.settings["door"]["on_time"] == door.on_time)
        tt.append(self.settings["door"]["off_time"] == door.off_time)
        tt.append(self.settings["door"]["switch_temp"] == door.switch_temp)

        if not all(tt):
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
