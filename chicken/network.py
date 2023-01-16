# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: network.py

Various network status and email control functions

"""

# Built-In Libraries
import logging
import os

# 3rd Party Libraries
import requests
import urllib3

# Internal Imports
from chicken import utils


WLAN = "en0" if utils.get_system_type() == "Darwin" else "wlan0"


class NetworkStatus:
    """Class for network status and update methods

    [extended_summary]
    """

    def __init__(self, logger: logging.Logger):

        # Use the passed-in logger
        self.logger = logger

        self.lan_ipv4 = "-----"
        self.wan_ipv4 = "-----"
        self.wifi_status = "UNKNOWN"
        self.inet_status = "UNKNOWN"

    def update_lan(self):
        """Update the LAN status variables

        [extended_summary]
        """
        self.lan_ipv4 = self.get_local_ipv4()
        if self.contact_server("192.168.0.1"):
            self.wifi_status = "ON"

            # For the Pi, add Link Quality
            if utils.get_system_type() != "Darwin":
                try:
                    qual = os.popen("/sbin/iwconfig wlan0 | grep -i quality").read()
                    qual = (qual.strip().split("  ")[1]).split("=")[1]
                except IndexError:
                    qual = "-- dBm"
                self.wifi_status = f"ON: {qual}"
        else:
            self.wifi_status = "OFF"

    def update_wan(self):
        """Update the WAN status variables

        [extended_summary]
        """
        self.inet_status = "ON" if self.contact_server("1.1.1.1") else "OFF"
        self.wan_ipv4 = self.get_public_ipv4()

    def contact_server(self, host="192.168.0.1"):
        """Check whether a server is reachable

        [extended_summary]

        Parameters
        ----------
        host : str, optional
            Name or IP address of server to contact (Default: "``192.168.0.1``")

        Returns
        -------
        bool
            Whether server is reachable
        """
        try:
            http = urllib3.PoolManager()
            http.request("GET", host, timeout=3, retries=False)
            return True
        except urllib3.exceptions.ConnectTimeoutError:
            self.logger.warning("Local router timeout error.")
        except Exception as error:
            self.logger.warning(
                "While contacting local router, urllib3 threw exception: %s %s",
                error,
                error.__class__.__name__,
            )
        return False

    @staticmethod
    def get_local_ipv4():
        """Return the local (LAN) IP address for the Pi

        Use ``ifconfig`` to read the local IP address assigned to the Pi by the
        local DHCP server.

        Returns
        -------
        str
            LAN IP address
        """
        cmd = f"/sbin/ifconfig {WLAN} | grep 'inet ' | awk '{{print $2}}'"
        return (os.popen(cmd).read()).strip()

    def get_public_ipv4(self):
        """Return the public-facing IP address for the Pi

        Query ipify.org to return the public (WAN) IP address for the network
        appliance to which the Chicken-Pi is attached.

        If an error message is kicked by ipify.org, then the response will be
        longer than the maximum 15 characters (xxx.xxx.xxx.xxx).  In this case,
        the function will return '-----' rather than an IP address.

        Returns
        -------
        str
            Public IP address
        """
        try:
            public_ipv4 = (
                requests.get("https://api.ipify.org", timeout=10).text
            ).strip()
            # If response is longer than the maximum 15 characters, return '---'.
            if len(public_ipv4) > 15:
                public_ipv4 = "-----"
        except requests.exceptions.Timeout:
            self.logger.warning("Public IPv4 timeout error.")
            public_ipv4 = "-----"
        except Exception as error:
            self.logger.warning(
                "While getting public IPv4, requests threw exception: %s %s",
                error,
                error.__class__.__name__,
            )
            public_ipv4 = "-----"
        return public_ipv4
