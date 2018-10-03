import logging
import sys


root=logging.getLogger("FeedTrough")


def get_logger(name):
  global root
  if name=="__main__" or name==None or name=="FeedTrough":
    return root
  child=root.getChild(name)
#  child.setLevel(logging.DEBUG)
  return child

def register_handler(default_level=logging.INFO):
  global root
  handler=logging.StreamHandler(sys.stderr)
  formatter=logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s')
  handler.setFormatter(formatter)
  root.addHandler(handler)
  root.setLevel(default_level)

