import os
import logging

# default logging setup to have some useful details
formatting = "[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] (L:%(lineno)s) %(module)s | %(funcName)s: %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=formatting,
)

# create the default logger
LOG = logging.getLogger()
