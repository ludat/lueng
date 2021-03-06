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
from InputServer import InputServer

logger = logging.getLogger('MAIN')


def main():
    Widget.loadAllWidgets()

    Widget.startAllWidgets()

    dzenProcess = subprocess.Popen(
        CONFIG['OUTPUT_CMD'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    inputServer = InputServer(Widget)

    widgetsInputHandler = WidgetsInputHandler(Widget, dzenProcess.stdin)

    widgetsOutputHandler = WidgetsOutputHandler(Widget, dzenProcess.stdout)

    inputServer.start()

    widgetsInputHandler.start()

    widgetsOutputHandler.start()

    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            widgetsInputHandler.kill()
            widgetsOutputHandler.kill()
            inputServer.kill()
            dzenProcess.terminate()
            Widget.killAllWidgets()
            return 0


if __name__ == "__main__":
    logger.debug("Program started")
    logger.debug(os.getcwd())
    main()
    logger.warning("Main thread is dead!")
