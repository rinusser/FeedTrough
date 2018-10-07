from abc import ABC
import unittest

from storage import *


class BaseStorageTest(ABC):
  """Abstract base class for Storage implementation tests.
  """

  @abstractmethod
  def _createStorage(self) -> Storage:
    """abstract: this should return a new storage instance to be tested

    :rtype: Storage
    """
    pass


  def testEmptyStorage(self):
    """Tests whether an empty storage doesn't find any contents.
    """
    storage=self._createStorage()

    self.assertEqual([],  storage.getFeeds(),         "empty storage should not have any contents")
    self.assertEqual(None,storage.getFeedByID(1),     "empty storage shouldn't find feed by ID")
    self.assertEqual([],  storage.getItemsByFeedID(1),"empty storage shouldn't find items by feed ID")


  def testPutFeed(self):
    """Tests whether .putFeed() stores data independently from live objects.
    """
    storage=self._createStorage()
    feed=Feed()
    feed.id=123
    feed.sourceName="test"
    feed.feedURL="uri://test"
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
    """Tests whether .putItem() properly adds items.
    """
    storage=self._createStorage()
    feed=Feed()
    feed.id=9
    feed.sourceName="test"
    feed.feedURL="uri://test"
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

