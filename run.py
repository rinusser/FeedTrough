from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

from domain import *
from scheduler import *
from storage import *
from source import *
from debug import *


next_item_id=1

def create_feed():
  global source
  feed=Feed()
  feed.sourceName="dummy"
  feed.feedURL="http://localhost:12356/feed/%s"%uuid4()
  feed.items=[]
  source.updateFeed(feed)
  sleep(0.11111)
  return feed

db=InMemoryStorage()
source=DummySource()

for i in range(1,4):
  feed=create_feed()
  db.putFeed(feed)

scheduler=StandaloneScheduler(db,[source])
scheduler.run()

print("done")
