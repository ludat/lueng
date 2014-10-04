#!/bin/env python3

import subprocess
import time
import logging

import os
import sys

from colors import colors
import configparser

from Engine import Widget
from WidgetsInputHandler import WidgetsInputHandler
from WidgetsOutputHandler import WidgetsOutputHandler

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd() + "/widgets.wanted/")


CONFIG = configparser.ConfigParser()
CONFIG.read('SB.conf')
SAFE_MODULES_ONLY = CONFIG['ENGINE'].getboolean('SAFE_MODULES_ONLY', True)

logger = logging.getLogger('Engine')
logger.setLevel(logging.DEBUG)
formatterString = (
    '{RESET}'
    '{RED}%(levelname)-7s{RESET}|'
    '{GREEN}{BOLD}%(name)s{RESET}|'
    '%(message)s{RESET}'.format(**colors))
formatter = logging.Formatter(formatterString)

# # Add FileHandler
# now = datetime.datetime.now()
# timeStamp = now.strftime("%Y-%m-%d_%H:%M:%S")
#
# fileLogHandler = logging.FileHandler("{}.statusBar.log".format(timeStamp))
# fileLogHandler.name = 'File Logger'
# fileLogHandler.level = logging.DEBUG
# fileLogHandler.formatter = formatter
# logger.addHandler(fileLogHandler)

# Add ConsoleHandler
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.name = 'Console Logger'
consoleLogHandler.level = logging.DEBUG
consoleLogHandler.formatter = formatter
logger.addHandler(consoleLogHandler)


def main():
    Widget.loadAllModules()

    Widget.startAll()

    dzenProcess = subprocess.Popen(
        ["dzen2",
            "-ta", "r",
            "-bg", "#161616",
            "-fn", "Terminus:size=8",
            "-w", "1300",
            "-x", "500",
            "-e", "",
            "-dock"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True)

    widgetsInputHandler = WidgetsInputHandler(Widget, dzenProcess.stdin)

    widgetsOutputHandler = WidgetsOutputHandler(Widget, dzenProcess.stdout)

    widgetsInputHandler.start()

    widgetsOutputHandler.start()

    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            widgetsInputHandler.kill()
            widgetsOutputHandler.kill()
            dzenProcess.terminate()
            Widget.killAll()
            return 0


if __name__ == "__main__":
    logger.debug("Program started")
    logger.debug(os.getcwd())
    main()
    logger.warning("Main thread is dead!")
