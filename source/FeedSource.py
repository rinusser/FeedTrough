from datetime import datetime, timedelta
import string
from time import strftime, sleep
from typing import List
import unittest

import feedparser

from domain import *
from logger import get_logger
from source import *
import testutils

#from debug import *


log=get_logger(__name__)


class FeedSource(Source):
  """An RSS/Atom feed source.
  """

  @property
  def name(self) -> str:
    """the unique source identifier for this source, 'feed'
    """
    return "feed"

  def updateFeed(self, feed:Feed) -> None:
    """refreshes an RSS/Atom feed from its feed URL

    :param Feed feed: the feed to update
    """
    result=feedparser.parse(feed.feedURL)

    update_minutes=60
    if "ttl" in result.feed:
      update_minutes=int(result.feed["ttl"])
    feed.updateInterval=timedelta(minutes=update_minutes)
    feed.title=result.feed["title"]
    if "subtitle" in result.feed:
      feed.description=result.feed["subtitle"]
    feed.websiteURL=result.feed["link"]
    feed.lastRefreshed=datetime.now()
    feed.lastChanged=self._parseDateTime(result.version,"updated",result.feed)

    for entry in result.entries:
      item=Item()
      item.feedID=feed.id
      if "title" in entry:
        item.title=entry["title"]
      if "summary" in entry:
        item.description=entry["summary"]
      if "link" in entry:
        item.itemURL=entry["link"]
      if "id" in entry:
        item.guid=entry["id"]
      item.publicationDate=self._parseDateTime(result.version,"updated",entry)
      if item.publicationDate==None:
        item.publicationDate=self._parseDateTime(result.version,"published",entry)
      self._mergeItem(feed,item)
#    dump_feed(feed)

  def _mergeItem(self,feed,item): #TODO: add test
    for ti,existing in enumerate(feed.items):
      log.debug("merge: comparing (%s,%s) against (%s,%s)",item.guid,item.itemURL,existing.guid,existing.itemURL)
      existing_id=existing.id
      if item.guid!=None:
        if item.guid!=existing.guid:
          log.debug("merge: guid mismatch, can't be same")
          continue
        else:
          log.debug("merge: guid match, updating")
          item.id=existing_id
          feed.items[ti]=item
          return
      if item.itemURL!=None:
        if item.itemURL!=existing.itemURL:
          log.debug("merge: itemURL mismatch, can't be same")
          continue
        else:
          log.debug("merge: itemURL match, updating")
          item.id=existing_id
          feed.items[ti]=item
          return
    log.debug("inserting item")
    feed.items.append(item)


  def _parseDateTime(self,version,key,source):
    if key in source and version=="rss20":
      input=self._convertTimezoneNameToOffset(source[key])
      return datetime.strptime(input,"%a, %d %b %Y %H:%M:%S %z")
    if key+"_parsed" in source:
      return datetime(*source[key+"_parsed"][:6])
    return None

  def _convertTimezoneNameToOffset(self, str):
    offsets={"UTC":"+0000","CEST":"+0200","CET":"+0100","EST":"-0500","EDT":"-0400"} #TODO: improve this
    for name in offsets:
      str=str.replace(" "+name," "+offsets[name])
    return str


class TestFeedSource(unittest.TestCase):
  """Tests for FeedSource.
  """

  @classmethod
  def setUpClass(clazz):
    """test class fixture, called by unittest
    """
    testutils.Server().start()
    sleep(0.2) #wait server thread to start


  def testMinimalRSS20(self):
    """Tests the basics of an RSS 2.0 feed.
    """
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss20.minimal.xml")
    self.assertEqual("Minimal RSS 2.0",feed.title)
    self.assertEqual("http://test/rss20.minimal",feed.websiteURL)
    self.assertEqual(2,len(feed.items))
    self.assertEqual("item 1",feed.items[0].title)
    self.assertEqual("desc 2",feed.items[1].description)

  def testFullRSS20(self):
    """Tests the optional fields in an RSS 2.0 feed.
    """
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss20.full.xml")
    self.assertEqual(123*60,             feed.updateInterval.total_seconds())
    self.assertEqual("ad space for rent",feed.description)
    self._assertUTCDate("2018-09-30 00:00:00",feed.lastChanged)

    self.assertEqual(2,len(feed.items))
    self.assertEqual("uri://feedtrough/rss20/full#1",feed.items[0].guid)
    self.assertEqual("http://test/rss20.full#1",     feed.items[0].itemURL)
    self._assertUTCDate("2018-09-29 10:34:56",feed.items[1].publicationDate)

  def testRSS10Dates(self):
    """Tests date formatting in an RSS 1.0 feed
    """
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss10.full.xml")
    self._assertUTCDate("2018-09-30 09:11:12",feed.lastChanged)
    self._assertUTCDate("2018-09-30 09:11:12",feed.items[0].publicationDate)
    self._assertUTCDate("2018-09-21 12:01:01",feed.items[2].publicationDate)

  def testAtom10(self):
    """Tests Atom 1.0 feeds
    """
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/atom10.example.xml")
    self.assertEqual("Atom 1.0",feed.title)
    self._assertUTCDate("2018-09-28 18:16:14",feed.lastChanged)
    self._assertUTCDate("2018-09-28 18:16:14",feed.items[0].publicationDate)
    self._assertUTCDate("2018-07-31 19:03:04",feed.items[1].publicationDate)
    self.assertEqual("title 2",             feed.items[1].title)
    self.assertEqual("http://test/atom10/2",feed.items[1].guid)

  def _assertUTCDate(self,expected,dt):
    self.assertEqual(expected,strftime("%Y-%m-%d %H:%M:%S",dt.utctimetuple()))

  def _readFeed(self,url):
    feed=Feed()
    feed.feedURL=url
    source=FeedSource()
    source.updateFeed(feed)
    return feed

