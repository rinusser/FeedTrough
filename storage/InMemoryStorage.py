from storage import *
from copy import deepcopy

class InMemoryStorage(Storage):
  feeds=[]

  def getFeeds(self):
    return self.feeds

  def getFeedByID(self, id):
    for feed in self.feeds:
      if feed.id==id:
        return feed
    return None

  def putFeed(self, feed):
    cp=deepcopy(feed)
    for ti,local in enumerate(self.feeds):
      if local.id==cp.id:
        self.feeds[ti]=cp
        return
    self.feeds.append(cp)

  def getItemsByFeedID(self, feed_id):
    feed=self.getFeedByID(feed_id)
    if feed==None:
      return []
    return feed.items

  def putItem(self, item):
    feed=self.getFeedByID(item.feedID)
    if feed==None:
      return
    feed.items.append(deepcopy(item))
