#!/bin/env python3

import os
import logging
from ast import literal_eval as meval

import collections

logger = logging.getLogger('CONFIG')


def update(d, u):
    for k, v in d.items():
        if isinstance(u[k], type(d[k])):
            if isinstance(v, collections.Mapping):
                d[k] = update(d.get(k, {}), u.get(k, {}))
            else:
                d[k] = u[k]
        else:
            logger.warning(
                "Data type mismatch {} != {}".format(
                    str(type(d[k])),
                    str(type(u[k]))
                )
            )
    return d

USER_CONFIG = {}
DEFAULT_CONFIG = {}
CONFIG = {}
CONFIG_FILE = os.path.expanduser('~/.config/SB/SB.conf.py')
try:
    with open(CONFIG_FILE) as configFile:
        data = configFile.read()
        USER_CONFIG = meval(data)
except FileNotFoundError as e:
    logger.warning(
        "{} doesn't exist. Failing to defaults".format(CONFIG_FILE))
    USER_CONFIG = {}
except ValueError as e:
    logger.warning(
        "{} is malformed. Failing to defaults".format(CONFIG_FILE))
    USER_CONFIG = {}
except Exception as e:
    raise e

with open('src/default.py') as defaultFile:
    data = defaultFile.read()
    DEFAULT_CONFIG = meval(data)

logger.debug("Merging default and custom config files")
CONFIG = update(DEFAULT_CONFIG, USER_CONFIG)
