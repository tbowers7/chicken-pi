# -*- coding: utf-8 -*-

"""
    MODULE: chicken-pi
    FILE: network.py

Various network status and email control functions

"""

# Built-In Libraries
import os

# 3rd Party Libraries
from requests import get
import urllib3

# Internal Imports

# Enable testing on both Raspberry Pi and Mac
if os.path.exists("/usr/bin/uname"):
    _UNAME = "/usr/bin/uname"
elif os.path.exists("/bin/uname"):
    _UNAME = "/bin/uname"
else:
    _UNAME = ""
SYSTYPE = (os.popen(f"{_UNAME} -a").read()).split()[0]
WLAN = 'en0' if SYSTYPE == 'Darwin' else 'wlan0'


class NetworkStatus():
    """NetworkStatus Class for network status and update methods

    [extended_summary]
    """
    def __init__(self):
        self.lan_ipv4 = ''
        self.wan_ipv4 = ''
        self.wifi_status = ''
        self.inet_status = ''

    def update_lan(self):
        """update_lan Update the LAN status variables

        [extended_summary]
        """
        self.lan_ipv4 = get_local_ipv4()
        if contact_server('192.168.0.1'):
            self.wifi_status = 'ON'

            # For the Pi, add Link Quality
            if SYSTYPE != 'Darwin':
                try:
                    qual = os.popen("/sbin/iwconfig wlan0 | grep -i quality").read()
                    qual = (qual.strip().split('  ')[1]).split("=")[1]
                except IndexError:
                    qual = '-- dBm'
                self.wifi_status = f"ON: {qual}"
        else:
            self.wifi_status = 'OFF'

    def update_wan(self):
        """update_wan Update the WAN status variables

        [extended_summary]
        """
        self.inet_status = 'ON' if contact_server('1.1.1.1') else 'OFF'
        self.wan_ipv4 = get_public_ipv4()


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
    except Exception as e:
        print(f"urllib3 threw exception: {e}")
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
    except Exception as e:
        print(f"requests threw exception: {e}")
        public_ipv4 = '-----'
    return public_ipv4
