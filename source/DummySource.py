from datetime import datetime, timedelta

from domain import *
from source import *


class DummySource(Source):
  feedURLs=[]
  update_count=0
  next_item_id=1

  @property
  def name(self):
    return "dummy"

  def updateFeed(self, feed):
    feed.id=self._getFeedID(feed)
    feed.updateInterval=timedelta(seconds=3*feed.id)
    feed.title="feed %d title"%feed.id
    feed.description="description for feed %d"%feed.id
    feed.websiteURL="http://does.not.exist/%d/blah"%feed.id
    feed.lastRefreshed=datetime.now()

    if self.update_count%2==0:
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


  def _createItem(self, feed):
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

  def _getFeedID(self, feed):
    try:
      id=self.feedURLs.index(feed.feedURL)+1
    except ValueError:
      self.feedURLs.append(feed.feedURL)
      id=len(self.feedURLs)
    return id

