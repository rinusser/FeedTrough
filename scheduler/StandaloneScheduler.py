from datetime import datetime, timedelta
from time import sleep
import unittest
from unittest.mock import patch

from domain import *
from scheduler import *
from source import *
from storage import *

from debug import *


class StandaloneScheduler(Scheduler):
  def run(self, iteration_limit:int=20) -> None:
    for i in range(0,iteration_limit):
      wait=self._checkAll()
#      dump_feeds(self.storage.getFeeds(),details=False)
#      print("waiting %5.2fs..."%wait)
      sleep(wait)
#    print("exiting scheduler")

  def _checkAll(self) -> float:
    feeds=self.storage.getFeeds()
    now=datetime.now()
    deltas=[]
    for feed in feeds:
      if feed.lastRefreshed!=None:
        next_update_at=feed.lastRefreshed+feed.updateInterval
      else:
        next_update_at=now
      next_update_delta=(next_update_at-now).total_seconds()
#      print("feed %d, lastRefreshed=%s, interval=%s => next update delta: %5.2f"%(feed.id,feed.lastRefreshed,feed.updateInterval,next_update_delta))
      if next_update_delta>0:
        deltas.append(next_update_delta)
      else:
        self._updateFeed(feed)
        deltas.append(feed.updateInterval.total_seconds())
    wait=min(deltas)
#    print("deltas: %s => waiting %s"%(deltas,wait))
    return wait

  def _updateFeed(self, feed:Feed):
    self.sources[feed.sourceName].updateFeed(feed)
    self.storage.putFeed(feed)


class TestStandaloneScheduler(unittest.TestCase):
  def testUpdateOrder(self):
    storage=InMemoryStorage()
    source=DummySource()
    now=datetime.now()
    self._storeFeed(source,storage,1,now,1)
    self._storeFeed(source,storage,3,now,2.5)

    scheduler=StandaloneScheduler(storage,[DummySource()])
    scheduler.keepUpdateInterval=True
    scheduler.run(6)

    actuals=storage.getFeeds()
    self.assertEqual(2,len(actuals),"self-check: should have 2 feeds stored")

    # The combination of feed update intervals, DummySource's sequential item ID generation and DummySource's adding of items on
    # every other refresh results in deterministic article assignment in feeds. This is tested for here.
    self._assertItemIDs([1,3],actuals[0])
    self._assertItemIDs([2],  actuals[1])

  def _storeFeed(self,source,storage,id,last_refreshed,update_interval):
    feed=Feed()
    feed.id=id
    source.updateFeed(feed,skip_items=True)
    feed.lastRefreshed=last_refreshed
    feed.updateInterval=timedelta(seconds=update_interval)
    storage.putFeed(feed)

  def _assertItemIDs(self,expected_ids,feed):
    actual=[]
    for item in feed.items:
      actual.append(item.id)
    self.assertEqual(expected_ids,actual,"list of item IDs should match")
