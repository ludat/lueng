#!/bin/python3

import logging
from Config import CONFIG
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
consoleLogHandler.formatter = formatter

logger = logging.getLogger('MAIN')
logger.setLevel(CONFIG['MAIN']['LOGGING_LEVEL'])
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('ENGINE')
logger.setLevel(CONFIG['ENGINE']['LOGGING_LEVEL'])
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('INPUT_WIDGET')
logger.setLevel(CONFIG['INPUT_WIDGET']['LOGGING_LEVEL'])
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('OUTPUT_WIDGET')
logger.setLevel(CONFIG['OUTPUT_WIDGET']['LOGGING_LEVEL'])
logger.addHandler(consoleLogHandler)

logger = logging.getLogger('INPUT_SERVER')
logger.setLevel(CONFIG['INPUT_SERVER']['LOGGING_LEVEL'])
logger.addHandler(consoleLogHandler)


formatterString = (
    '{RESET}'
    '{RED}{BOLD}%(levelname)-7s{RESET}:'
    '{GREEN}{BOLD}W{RESET}:'
    '{YELLOW}{BOLD}%(threadName)-15s{RESET}:'
    '%(message)s{RESET}'.format(**colors))
formatter = logging.Formatter(formatterString)

# Add ConsoleHandler
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.name = 'Console Logger'
consoleLogHandler.formatter = formatter

logger = logging.getLogger('WIDGET')
logger.setLevel(CONFIG['WIDGET']['LOGGING_LEVEL'])
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
