import logging
import os
import sys
from pathlib import Path

import environ
from loguru import logger

env = environ.Env()

DEBUG = env.bool("POF_DEBUG", default=False)
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_POF_DIR = Path.home() / ".pof"
POF_DIR = Path(env.path("POF_DIR", default=DEFAULT_POF_DIR))

COLOR_MAIN = "#fdca40"
COLOR_ACCENT = "#3aaed8"
# COLOR_ACCENT = "#d75fd7"  # orchid
COLOR_ERROR = "#f64740"

ICON_POF = "🚥"
ICON_POFV = "🚦"
ICON_INFO = "💡"
ICON_ERROR = "🍄‍🟫"
ICON_MULTI_ERROR = "🍄"
ICON_STATUS = "•"

FAILFAST_DELAY = 2
DATETIME_FORMAT = "%H:%M:%S %Y/%m/%d"
TRUNCATE_LENGTH = 36
RESTART_DELIM = "@"

# watcher settings
# TODO: enable by default once ready
POFW_ENABLED = env.bool("POFW_ENABLED", default=False)

logger.remove()
if DEBUG:
    logger.add(sys.stderr, level=logging.DEBUG)
