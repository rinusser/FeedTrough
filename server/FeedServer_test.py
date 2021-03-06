import unittest

import feedparser

from server import *
from storage import *


class TestFeedServer(unittest.TestCase):
  """Tests for FeedServer.
  """

  @classmethod
  def setUpClass(clazz):
    """test class fixture, called by unittest.
    """
    storage=InMemoryStorage()
    feed1=Feed(id=10,title="feed 10")
    storage.putFeed(feed1)

    feed2=Feed(id=20,title="feed 20")
    item21=Item(id=201,feedID=20,title="title 20.1")
    feed2.items.append(item21)
    item22=Item(id=202,feedID=20,title="title 20.2")
    item22.description="\u00ef\u4eba"
    feed2.items.append(item22)
    storage.putFeed(feed2)

    FeedServer(storage).start()


  def testFeedPresentation(self):
    """Tests whether feeds are hosted correctly.
    """
    result1=self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/10",200,"first feed should be found")
    self.assertEqual("feed 10",result1.feed.title,  "first feed title should match")
    self.assertEqual(0,        len(result1.entries),"first feed shouldn't contain any items")

    result2=self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/20",200,"second feed should be found")
    self.assertEqual("feed 20",     result2.feed.title,            "second feed title should match")
    self.assertEqual(2,             len(result2.entries),          "second feed should have exactly 2 items")
    self.assertEqual("title 20.2",  result2.entries[1].title,      "second feed's second item title should match")
    self.assertEqual("\u00ef\u4eba",result2.entries[1].description,"UTF-8 data should be encoded properly")


  def testOptionalFeedURLSuffix(self):
    """Tests whether feed URLs can be suffixed, e.g. to add a feed name.
    """
    self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/10/ignore/kthx",200,"trailer after feed ID should be ignored")
    self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/101",           404,"partially known ID string shouldn't match")


  def testErrors(self):
    """Tests whether the server produces the correct errors for invalid URLs.
    """
    self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/1",404,"no feed with this ID should be found")
    self._fetchAndAssertStatus("http://127.0.0.1:58000/feed/a",400,"non-numeric feed ID should produce status 400")
    self._fetchAndAssertStatus("http://127.0.0.1:58000/3",     404,"other URLs should produce status 404")


  def _fetchAndAssertStatus(self, url:str, status:int, message:str):
    result=feedparser.parse(url)
    self.assertEqual(status,result.status,message)
    return result

