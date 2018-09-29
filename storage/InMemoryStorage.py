from typing import List,Union
import unittest

from domain import *
from storage import *
from copy import deepcopy


class InMemoryStorage(Storage):
  feeds=[]

  def __init__(self):
    self.feeds=[]

  def getFeeds(self) -> List[Feed]:
    return self.feeds

  def getFeedByID(self, id:int) -> Union[Feed,None]:
    for feed in self.feeds:
      if feed.id==id:
        return feed
    return None

  def putFeed(self, feed:Feed) -> None:
    cp=deepcopy(feed)
    for ti,local in enumerate(self.feeds):
      if local.id==cp.id:
        self.feeds[ti]=cp
        return
    self.feeds.append(cp)

  def getItemsByFeedID(self, feed_id:int) -> List[Item]:
    feed=self.getFeedByID(feed_id)
    if feed==None:
      return []
    return feed.items

  def putItem(self, item:Item) -> None:
    feed=self.getFeedByID(item.feedID)
    if feed==None:
      return
    feed.items.append(deepcopy(item))


class TestInMemoryStorage(unittest.TestCase):
  def testEmptyStorage(self):
    storage=InMemoryStorage()

    self.assertEqual([],  storage.getFeeds(),         "empty storage should not have any contents")
    self.assertEqual(None,storage.getFeedByID(1),     "empty storage shouldn't find feed by ID")
    self.assertEqual([],  storage.getItemsByFeedID(1),"empty storage shouldn't find items by feed ID")


  def testMultipleStorageSeparation(self):
    storage1=InMemoryStorage()
    storage2=InMemoryStorage()
    feed=Feed()
    feed.id=2
    feed.title="asdf"
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


  def testPutFeed(self):
    storage=InMemoryStorage()
    feed=Feed()
    feed.id=123
    feed.title="original feed title"

    item1=Item()
    item1.id=456
    item1.title="original item title"
    feed.items=[item1]

    storage.putFeed(feed)

    feed.id=78
    feed.title="lalala"
    item1.id=90
    item1.title="meh"
    feed.items.append(Item())

    stored=storage.getFeedByID(123)
    self.assertEqual(123,                  stored.id,   "feed ID shouldn't have changed")
    self.assertEqual("original feed title",stored.title,"feed title shouldn't have changed")

    self.assertEqual(1,                    len(stored.items),    "number of items shouldn't have changed")
    self.assertEqual(456,                  stored.items[0].id,   "stored item ID shouldn't have changed")
    self.assertEqual("original item title",stored.items[0].title,"stored item title shouldn't have changed")


  def testPutItem(self):
    storage=InMemoryStorage()
    feed=Feed()
    feed.id=9
    item1=Item()
    item1.id=11
    item1.feedID=9
    feed.items=[item1]
    storage.putFeed(feed)

    item2=Item()
    item2.id=12
    item2.feedID=9
    storage.putItem(item2)

    stored=storage.getFeedByID(9)
    self.assertEqual(2, len(stored.items), "stored feed should have gotten additional item")
    self.assertEqual(11,stored.items[0].id,"pre-existing item should have same ID as before")
    self.assertEqual(12,stored.items[1].id,"manually stored item should have expected ID")

