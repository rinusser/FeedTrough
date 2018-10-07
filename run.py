from datetime import datetime, timedelta
import logging
from time import sleep
from uuid import uuid4

from domain import *
import logger
from scheduler import *
from storage import *
from server import *
from source import *
from debug import *
import config


def run():
  log=logger.get_logger(__name__)
  logger.register_handler(logging.INFO)
  next_feed_id=1

#  db=InMemoryStorage()
  db=SQLiteStorage("feeds.sqlite")
  sources=[DummySource(),FeedSource()]

  for type,url in config.sources:
    log.info("got source type %s: %s",type,url)
    feed=Feed()
    feed.id=next_feed_id
    next_feed_id+=1
    feed.sourceName=type
    feed.feedURL=url
    feed.updateInterval=timedelta(minutes=5)
    db.putFeed(feed)

  scheduler=StandaloneScheduler(db,sources)
  scheduler.start()

  server=FeedServer(db)
  server.start()

  try:
    sleep(60)
  except KeyboardInterrupt:
    pass

  log.info("exiting application")


if __name__=="__main__":
  run()

