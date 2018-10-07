import logging
import unittest

import logger
from scheduler import *
from server import *
from source import *
from storage import *


def run():
  log=logger.get_logger(__name__)
  logger.register_handler(logging.NOTSET)

  unittest.main(verbosity=1)


if __name__=="__main__":
  run()
