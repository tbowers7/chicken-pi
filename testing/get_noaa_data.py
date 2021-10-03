#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  FILE: get_noaa_data.py

Initial test routine for how to download NOAA data

"""

# Futures
# […]

# Built-in/Generic Imports
import os,sys              # Search for file on disk
# […]

# Libs
# […]

# Own modules
#from {path} import {class}
sys.path.append('NOAA_API_v2')      # This package sits in a subdir
from noaa_api_v2 import NOAAData    # NOAA API

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 1 - Planning'



# Load the API token from file
ABSPATH = os.path.abspath(os.path.dirname(sys.argv[0]))
with open(ABSPATH+'/.noaa_token.txt','r') as fileobj:
    for line in fileobj:
        TOKEN = line.rstrip()


### Set up the data structure
data = NOAAData(TOKEN)

# categories = data.data_categories(locationid='FIPS:37', sortfield='name')

# for i in categories:
#     print(i)

# locations = data.stations(0,0,sortfield='name',limit=25,stationid='USW00003103')

# for j in locations:
#     print(j)

# print(len(locations))

# weather_data = data.fetch_data(stationid='GHCND:USW00003103', datasetid='GHCND', startdate='2019-10-10', enddate='2020-01-31', limit=1000)

# for k in weather_data:
#     if k['datatype'] == 'TMAX':
#         print(k['date'],k['value'])
#     if k['datatype'] == 'TMIN':
#         print(k['date'],k['value'])


# print('-'*20)
# print(weather_data[0])

# print(type(weather_data[0]))
# print(weather_data[0].items())

# print(weather_data[0]['datatype'])

print('-'*20)
dtypes = data.data_types(limit=1000,stationid='GHCND:USW00003103')
print(dtypes[0])
for i in dtypes:
    if i['id'] == 'TOBS':
        print(i['date'],i['id'],i['value'])
