import os
import logging
from ast import literal_eval as meval


logger = logging.getLogger('CONFIG')

CONFIG = {}
CONFIG_FILE = os.path.expanduser('~/.config/SB/SB.conf.py')
try:
    with open(CONFIG_FILE) as configFile:
        data = configFile.read()
        CONFIG = meval(data)
except FileNotFoundError as e:
    logger.warn(
        "{} doesn\' exist. Failing to defaults".format(CONFIG_FILE))
    CONFIG = {}
except ValueError as e:
    logger.warn(
        "{} is malformed. Failing to defaults".format(CONFIG_FILE))
    CONFIG = {}
except Exception as e:
    raise e

with open('src/default.py') as defaultFile:
    data = defaultFile.read()
    CONFIG = meval(data)
