from datetime import datetime, timedelta
import string
from time import strftime
from typing import List
import unittest

import feedparser

from domain import *
from source import *
import testutils


class FeedSource(Source):
  @property
  def name(self) -> str:
    return "feed"

  def updateFeed(self, feed:Feed) -> None:
    result=feedparser.parse(feed.feedURL)
#    print(result)

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

    feed.items=[]
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
  @classmethod
  def setUpClass(clazz):
    testutils.Server().start()

  def testMinimalRSS20(self):
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss20.minimal.xml")
    self.assertEqual("Minimal RSS 2.0",feed.title)
    self.assertEqual("http://test/rss20.minimal",feed.websiteURL)
    self.assertEqual(2,len(feed.items))
    self.assertEqual("item 1",feed.items[0].title)
    self.assertEqual("desc 2",feed.items[1].description)

  def testFullRSS20(self):
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss20.full.xml")
    self.assertEqual(123*60,             feed.updateInterval.total_seconds())
    self.assertEqual("ad space for rent",feed.description)
    self._assertUTCDate("2018-09-30 00:00:00",feed.lastChanged)

    self.assertEqual(2,len(feed.items))
    self.assertEqual("uri://feedtrough/rss20/full#1",feed.items[0].guid)
    self.assertEqual("http://test/rss20.full#1",     feed.items[0].itemURL)
    self._assertUTCDate("2018-09-29 10:34:56",feed.items[1].publicationDate)

  def testRSS10Dates(self):
    feed=self._readFeed("http://127.0.0.1:58050/testresources/feeds/rss10.full.xml")
    self._assertUTCDate("2018-09-30 09:11:12",feed.lastChanged)
    self._assertUTCDate("2018-09-30 09:11:12",feed.items[0].publicationDate)
    self._assertUTCDate("2018-09-21 12:01:01",feed.items[2].publicationDate)

  def testAtom10(self):
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

