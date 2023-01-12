# -*- coding: utf-8 -*-
#
#  Created on 12-Jan-2023
#
#  @author: tbowers

"""

"""

# Built-In Libraries
import pathlib

# 3rd Party Libraries
from pkg_resources import resource_filename

# Internal Imports


# Classes to hold useful information
class Paths:
    """Class that holds the various paths needed"""

    # Main data & config directories
    resources = pathlib.Path(resource_filename("chicken", "resources"))
    data = pathlib.Path(resource_filename("chicken", "data"))
