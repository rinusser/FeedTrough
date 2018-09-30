from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

from domain import *
from scheduler import *
from storage import *
from source import *
from debug import *
import config


next_feed_id=1

db=InMemoryStorage()
sources=[DummySource(),FeedSource()]

for type,url in config.sources:
  print("got source type %s: %s"%(type,url))
  feed=Feed()
  feed.id=next_feed_id
  next_feed_id+=1
  feed.sourceName=type
  feed.feedURL=url
  feed.updateInterval=timedelta(minutes=5)
  db.putFeed(feed)

scheduler=StandaloneScheduler(db,sources)
scheduler.run()

print("done")
