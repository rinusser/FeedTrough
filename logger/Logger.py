import logging
import sys


root=logging.getLogger("FeedTrough")


def get_logger(name:str) -> logging.Logger:
  """Returns a hierarchical logger relative to FeedTrough's main module.

  :param str name: the logger's name
  :return: the logger instance
  :rtype: logging.Logger
  """
  global root
  if name=="__main__" or name==None or name=="FeedTrough":
    return root
  child=root.getChild(name)
#  child.setLevel(logging.DEBUG)
  return child


def register_handler(default_level=logging.INFO):
  """Add the default logging handler. Do not call if you want to use your own log handlers.

  :param default_level: the default log level to use (default: logging.INFO)
  """
  global root
  handler=logging.StreamHandler(sys.stderr)
  formatter=logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s')
  handler.setFormatter(formatter)
  root.addHandler(handler)
  root.setLevel(default_level)

