#!/bin/env python3
import os
import sys

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd() + "/widgets.wanted/")

import CustomLoggers
from Config import CONFIG
CONFIG = CONFIG['MAIN']

import subprocess
import time
import logging

from Engine import Widget
from WidgetsInputHandler import WidgetsInputHandler
from WidgetsOutputHandler import WidgetsOutputHandler

logger = logging.getLogger('MAIN')


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
