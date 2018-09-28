from datetime import datetime
from time import sleep

from domain import *
from scheduler import *
from debug import *


class StandaloneScheduler(Scheduler):
  def run(self):
    for i in range(1,20):
      wait=self._checkAll()
      dump_feeds(self.storage.getFeeds(),details=False)
      print("waiting %5.2fs..."%wait)
      sleep(wait)
    print("exiting scheduler")

  def _checkAll(self):
    feeds=self.storage.getFeeds()
    now=datetime.now()
    deltas=[]
    for feed in feeds:
      next_update_at=feed.lastRefreshed+feed.updateInterval
      next_update_delta=(next_update_at-now).total_seconds()
      print("feed %d, lastRefreshed=%s, interval=%s => next update delta: %5.2f"%(feed.id,feed.lastRefreshed,feed.updateInterval,next_update_delta))
      if next_update_delta>0:
        deltas.append(next_update_delta)
      else:
        self._updateFeed(feed)
        deltas.append(feed.updateInterval.total_seconds())
    wait=min(deltas)
    print("deltas: %s => waiting %s"%(deltas,wait))
    return wait

  def _updateFeed(self,feed):
    self.sources[feed.sourceName].updateFeed(feed)
    self.storage.putFeed(feed)

