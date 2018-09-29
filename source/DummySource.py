from datetime import datetime, timedelta
from typing import List
import unittest

from domain import *
from source import *


class DummySource(Source):
  feedURLs=[]
  update_count=0
  next_item_id=1
  keepUpdateInterval=False

  @property
  def name(self) -> str:
    return "dummy"

  def updateFeed(self, feed:Feed, skip_items=False) -> None:
    feed.id=self._getFeedID(feed)
    if not self.keepUpdateInterval:
      feed.updateInterval=timedelta(seconds=feed.id)
    feed.title="feed %d title"%feed.id
    feed.description="description for feed %d"%feed.id
    feed.websiteURL="http://does.not.exist/%d/blah"%feed.id
    feed.lastRefreshed=datetime.now()
    feed.sourceName=self.name

    if self.update_count%2==0 and not skip_items:
      feed.items.append(self._createItem(feed))
    self.update_count+=1

    if len(feed.items)>1:
      max=feed.items[0].publicationDate
      for item in feed.items[1:]:
        if item.publicationDate>max:
          max=item.publicationDate
      feed.lastChanged=max
    elif feed.lastChanged==None:
      feed.lastChanged=feed.lastRefreshed


  def _createItem(self, feed:Feed) -> Item:
    item=Item()
    item.id=self.next_item_id
    self.next_item_id+=1
    item.feedID=feed.id
    item.guid="urn://feedtrough/%d/%d"%(feed.id,item.id)
    item.title="item %d title"%item.id
    item.description="description for item %d"%item.id
    item.itemURL="http://localhost:12356/feed/%d/item/%d"%(feed.id,item.id)
    item.publicationDate=datetime.now()
    return item

  def _getFeedID(self, feed:Feed) -> int:
    if feed.id!=None:
      return feed.id

    try:
      id=self.feedURLs.index(feed.feedURL)+1
    except ValueError:
      self.feedURLs.append(feed.feedURL)
      id=len(self.feedURLs)

    return id


class TestDummySource(unittest.TestCase):
  def testItemIDUniqueness(self):
    feed=Feed()
    feed.id=15
    source=DummySource()
    for tc in range(0,10):
      source.updateFeed(feed)
    ids=[]
    for item in feed.items:
      ids.append(item.id)

    self._assertHasEnoughItemsForTest(ids)
    self.assertEqual(len(feed.items),len(set(ids)),"amount of feed items should equal number of unique IDs")

  def _assertHasEnoughItemsForTest(self, items):
    self.assertGreater(len(items),2,"self-check: there should be at least 3 items available")


  def testFeedIDIsSetCorrectly(self):
    feed1=Feed()
    feed1.id=20
    feed2=Feed()
    feed2.id=21
    source=DummySource()

    for tc in range(0,10):
      source.updateFeed(feed1)
      source.updateFeed(feed1)
      source.updateFeed(feed2)

    self._assertHasEnoughItemsForTest(feed1.items)
    self._assertHasEnoughItemsForTest(feed2.items)
    self._assertOnlyFeedIDIs(20,feed1.items)
    self._assertOnlyFeedIDIs(21,feed2.items)

  def _assertOnlyFeedIDIs(self, expectation:int, items:List[Item]):
    feed_ids=[]
    for item in items:
      feed_ids.append(item.feedID)
    self.assertEqual({expectation},set(feed_ids))

