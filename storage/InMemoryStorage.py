from typing import List,Union
import unittest

from domain import *
from storage import *
from copy import deepcopy


class InMemoryStorage(Storage):
  """Non-persistent storage implementation.

  This storage adapter keeps feeds and items in memory only: upon application shutdown all data is lost.
  """
  _feeds=[]

  def __init__(self):
    self._feeds=[]

  def getFeeds(self) -> List[Feed]:
    """returns a list of all feeds
    """
    return self._feeds

  def getFeedByID(self, id:int) -> Union[Feed,None]:
    """looks up an individual feed by ID
    """
    for feed in self._feeds:
      if feed.id==id:
        return feed
    return None

  def putFeed(self, feed:Feed) -> None:
    """stores an individual feed
    """
    cp=deepcopy(feed)
    for ti,local in enumerate(self._feeds):
      if local.id==cp.id:
        self._feeds[ti]=cp
        return
    self._feeds.append(cp)

  def getItemsByFeedID(self, feed_id:int) -> List[Item]:
    """looks up a feed's items
    """
    feed=self.getFeedByID(feed_id)
    if feed==None:
      return []
    return feed.items

  def putItem(self, item:Item) -> None:
    """stores an individual item, if the parent feed is stored already
    """
    feed=self.getFeedByID(item.feedID)
    if feed==None:
      return
    feed.items.append(deepcopy(item))


class TestInMemoryStorage(BaseStorageTest,unittest.TestCase):
  """Tests for the InMemoryStorage class.
  """

  def _createStorage(self):
    return InMemoryStorage()

  def testMultipleStorageSeparation(self):
    """Tests whether multiple instances keep separate data.
    """
    storage1=self._createStorage()
    storage2=self._createStorage()
    feed=Feed(id=2,sourceName="test",feedURL="uri://test",title="asdf")
    feed.items=[Item()]
    storage1.putFeed(feed)

    contents1=storage1.getFeeds()
    self.assertEqual(1,     len(contents1),         "filled storage should find the feed")
    self.assertEqual(2,     contents1[0].id,        "stored .id should match input")
    self.assertEqual("asdf",contents1[0].title,     "stored .title should match input")
    self.assertEqual(1,     len(contents1[0].items),"number of stored items should match")

    self.assertEqual(contents1[0],storage1.getFeedByID(2),          "should find stored feed by ID")
    self.assertEqual(1,           len(storage1.getItemsByFeedID(2)),"should find stored feed's items by feed ID")

    self.assertEqual([],  storage2.getFeeds(),         "other storage should still be empty")
    self.assertEqual(None,storage2.getFeedByID(2),     "other storage shouldn't find feed by ID")
    self.assertEqual([],  storage2.getItemsByFeedID(2),"other storage shouldn't find feed items by feed ID")

