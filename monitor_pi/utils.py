# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.#
#
#  Created on 10-Apr-2022
#
#  @author: tbowers

"""
    MODULE: monitor_pi
    FILE: utils.py

Various network status and email control functions

"""

# Built-In Libraries
import os

# 3rd Party Libraries

# Internal Imports


# Enable testing on both Raspberry Pi and Mac
if os.path.exists("/usr/bin/uname"):
    _UNAME = "/usr/bin/uname"
elif os.path.exists("/bin/uname"):
    _UNAME = "/bin/uname"
else:
    _UNAME = ""
SYSTYPE = (os.popen(f"{_UNAME} -a").read()).split()[0]
WLAN = "en0" if SYSTYPE == "Darwin" else "wlan0"
