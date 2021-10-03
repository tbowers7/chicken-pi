# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: database.py

Database routines for saving readings from the chicken-pi

"""

# Built-In Libraries
import atexit
import datetime

# 3rd Party Libraries
from astropy.table import Table
import numpy as np

# Internal Imports

@atexit.register
def write_database():
    pass
