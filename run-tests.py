import logging
import unittest

import logger
from scheduler import *
from server import *
from source import *
from storage import *

log=logger.get_logger(__name__)
logger.register_handler(logging.NOTSET)

unittest.main()

