# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: utils.py

Utility functions

"""

# Built-In Libraries
import os
import pathlib

# 3rd Party Libraries
from pkg_resources import resource_filename
import yaml

# Internal Imports


# Classes to hold useful information
class Paths:
    """Class that holds the various paths needed"""

    # Main data & config directories
    resources = pathlib.Path(resource_filename("chicken", "resources"))
    data = pathlib.Path(resource_filename("chicken", "data"))
    config = pathlib.Path(resource_filename("chicken", "config"))


def load_yaml_config():
    """load_yaml_config _summary_

    _extended_summary_

    Returns
    -------
    _type_
        _description_
    """

    with open(Paths.config.joinpath("config.yaml"), "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def get_system_type():
    """get_system_type _summary_

    _extended_summary_

    Returns
    -------
    _type_
        _description_
    """
    # Enable testing on both Raspberry Pi and Mac
    if os.path.exists("/usr/bin/uname"):
        uname = "/usr/bin/uname"
    elif os.path.exists("/bin/uname"):
        uname = "/bin/uname"
    else:
        uname = ""
    return (os.popen(f"{uname} -a").read()).split()[0]


if __name__ == "__main__":
    config = load_yaml_config()
    print(config)
    print(type(config))
