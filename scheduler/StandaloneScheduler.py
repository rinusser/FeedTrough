from datetime import datetime, timedelta
from time import sleep
import unittest
from unittest.mock import patch

from domain import *
import logger
from scheduler import *
from source import *
from storage import *

from debug import *


log=logger.get_logger(__name__)


class StandaloneScheduler(Scheduler):
  """A basic scheduler implementation.

  This scheduler reads each feed's last update time and waits until the feed's update interval has passed, then updates the feed from the appropriate source.
  """

  def run(self, iteration_limit:int=0) -> None:
    """Starts the scheduler.

    Schedulers are threads: unless you're testing the scheduler you'll probably want to call .start() instead.

    :param int iteration_limit: how many iterations to perform, <=0 for no limit.
    """

    i=0
    while True:
      log.debug("starting scheduler iteration...")
      wait=self._checkAll()
      if wait==None:
        return
#      dump_feeds(self.storage.getFeeds(),details=False)
#      print("waiting %5.2fs..."%wait)
      i=i+1
      if iteration_limit>0 and i>=iteration_limit:
        break
      sleep(wait)
    log.info("reached iteration limit, exiting scheduler")

  def _checkAll(self) -> float:
    feeds=self._storage.getFeeds()
    now=datetime.now()
    deltas=[]
    for feed in feeds:
      if feed.updateInterval==None:
        continue
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
    if len(deltas)<1:
      log.warn("no more feeds to update, exiting scheduler")
      return None
    wait=min(deltas)
#    print("deltas: %s => waiting %s"%(deltas,wait))
    return wait

  def _updateFeed(self, feed:Feed):
    self._sources[feed.sourceName].updateFeed(feed)
    self._storage.acquireWriteLock()
    self._storage.putFeed(feed)
    self._storage.releaseWriteLock()


class TestStandaloneScheduler(unittest.TestCase):
  """Tests for StandaloneScheduler
  """

  def testUpdateOrder(self):
    """Tests whether the scheduler updates feeds in the correct order.

    The combination of feed update intervals, DummySource's sequential item GUID generation and DummySource's adding of items on
    every other refresh results in deterministic article assignment in feeds. This is tested for here.
    """
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

    self._assertItemIDs([1,3],actuals[0])
    self._assertItemIDs([2],  actuals[1])

  def _storeFeed(self,source,storage,id,last_refreshed,update_interval):
    feed=Feed(id=id)
    source.updateFeed(feed,skip_items=True)
    feed.lastRefreshed=last_refreshed
    feed.updateInterval=timedelta(seconds=update_interval)
    storage.putFeed(feed)

  def _assertItemIDs(self,expected_ids,feed):
    actual=[]
    for item in feed.items:
      actual.append(int(item.guid[item.guid.rindex("/")+1:]))
    self.assertEqual(expected_ids,actual,"list of item IDs should match")
