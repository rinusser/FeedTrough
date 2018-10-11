from datetime import datetime, timedelta
from typing import List
import unittest

from domain import *
from source import *


class DummySource(Source):
  """A dummy data source, generates deterministic data that's probably useless outside of tests.
  """

  _feedURLs=[]
  _update_count=0
  _next_item_guid=1
  keepUpdateInterval=False  #: whether to keep the feed's original update intervals (default: False)

  @property
  def name(self) -> str:
    """the identifier for this source, 'dummy'
    """
    return "dummy"

  def updateFeed(self, feed:Feed, skip_items=False) -> None:
    """Updates the given feed.

    Items are added on every other invocation of this method, regardless of which feed is passed.

    :param Feed feed: the feed to update
    :param bool skip_items: whether to skip adding items (default: False)
    """
    feed.id=self._getFeedID(feed)
    if not self.keepUpdateInterval:
      feed.updateInterval=timedelta(seconds=feed.id)
    feed.title="feed %d title"%feed.id
    feed.description="description for feed %d"%feed.id
    feed.websiteURL="http://does.not.exist/%d/blah"%feed.id
    feed.lastRefreshed=datetime.now()
    feed.sourceName=self.name

    if self._update_count%2==0 and not skip_items:
      feed.items.append(self._createItem(feed))
    self._update_count+=1

    if len(feed.items)>1:
      max=feed.items[0].publicationDate
      for item in feed.items[1:]:
        if max==None or item.publicationDate!=None and item.publicationDate>max:
          max=item.publicationDate
      feed.lastChanged=max
    elif feed.lastChanged==None:
      feed.lastChanged=feed.lastRefreshed


  def _createItem(self, feed:Feed) -> Item:
    item=Item()
    item.feedID=feed.id
    id=self._next_item_guid
    self._next_item_guid+=1
    item.guid="urn://feedtrough/%d/%d"%(feed.id,id)
    item.title="item %d title"%id
    item.description="description for item %d"%id
    item.itemURL="http://localhost:12356/feed/%d/item/%d"%(feed.id,id)
    item.publicationDate=datetime.now()
    return item

  def _getFeedID(self, feed:Feed) -> int:
    if feed.id!=None:
      return feed.id

    try:
      id=self._feedURLs.index(feed._feedURL)+1
    except ValueError:
      self._feedURLs.append(feed._feedURL)
      id=len(self._feedURLs)

    return id


class TestDummySource(unittest.TestCase):
  """Tests for DummySource.
  """

  def testItemGUIDUniqueness(self):
    """Tests whether generated item GUIDs are unique.
    """
    feed=Feed(id=15)
    source=DummySource()
    for tc in range(0,10):
      source.updateFeed(feed)
    guids=[]
    for item in feed.items:
      guids.append(item.guid)

    self._assertHasEnoughItemsForTest(guids)
    self.assertEqual(len(feed.items),len(set(guids)),"amount of feed items should equal number of unique GUIDs")

  def _assertHasEnoughItemsForTest(self, items):
    self.assertGreater(len(items),2,"self-check: there should be at least 3 items available")


  def testFeedIDIsSetCorrectly(self):
    """Tests whether items' feed ID is set correctly.
    """
    feed1=Feed(id=20)
    feed2=Feed(id=21)
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

