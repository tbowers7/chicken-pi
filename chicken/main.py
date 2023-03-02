# -*- coding: utf-8 -*-

"""
    MODULE: chicken
    FILE: main.py

Main driver routine for the integrated Chicken-Pi setup.

"""

# Built-In Libraries
import argparse
import atexit
import logging
import sys
import tkinter as tk

# 3rd Party Libraries

# Internal Imports
from chicken.control import ControlWindow
from chicken import utils


# ===================================================================#
def main(verbose=False):
    """
    Main function
    """

    # Set up logging
    logpath = utils.Paths.logs
    logging.basicConfig(
        filename=logpath.joinpath("chicken-pi.log"),
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.DEBUG if verbose else logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("chicken_log")
    logger.info("=" * 40)
    logger.info("Starting Program")

    # Set up the GUI
    root_tk_object = tk.Tk()
    control_window = ControlWindow(root_tk_object, logger)
    atexit.register(control_window.write_database_to_disk)

    # Begin the loop
    try:
        control_window.update()
        root_tk_object.mainloop()
    finally:
        root_tk_object.after_cancel(control_window.after_id)
        logger.info("Exiting Program")

    # Return success
    return 0


def entry_point():
    """entry_point

    _extended_summary_
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog="chickenpi",
        description="Control Software for the Chicken-Pi",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Use verbose (DEBUG level) logging",
    )
    args = parser.parse_args()

    # Giddy Up!
    sys.exit(main(args.verbose))


if __name__ == "__main__":
    entry_point()
