#!/bin/python3

import logging
from colors import colors

formatterString = (
    '{RESET}'
    '{RED}{BOLD}%(levelname)-7s{RESET}:'
    '{GREEN}{BOLD}%(name)-10s{RESET}:'
    '%(message)s{RESET}'.format(**colors))
formatter = logging.Formatter(formatterString)

# Add ConsoleHandler
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.name = 'Console Logger'
consoleLogHandler.level = logging.DEBUG
consoleLogHandler.formatter = formatter

logger = logging.getLogger('MAIN')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('CONFIG')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('ENGINE')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('WIDGET')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('INPUT_WIDGET')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('OUTPUT_WIDGET')
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleLogHandler)

# # Add FileHandler
# now = datetime.datetime.now()
# timeStamp = now.strftime("%Y-%m-%d_%H:%M:%S")
#
# fileLogHandler = logging.FileHandler("{}.statusBar.log".format(timeStamp))
# fileLogHandler.name = 'File Logger'
# fileLogHandler.level = logging.DEBUG
# fileLogHandler.formatter = formatter
# logger.addHandler(fileLogHandler)

