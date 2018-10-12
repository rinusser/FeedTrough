import sqlite3
from datetime import datetime, timedelta, timezone
import os
import sys
from time import sleep
from threading import local, Timer
from typing import List, Union
import unittest

from domain import *
from logger import get_logger
from storage import *


log=get_logger(__name__)


class SQLiteStorage(Storage):
  """Persistent storage implementation using an SQLite backend.

  This is safe for use in multithreaded environments. Each thread will open its own connection handle to the database file, as
  a result the sqlite's special ":memory:" file won't work across multiple threads - use a temporary local file instead.
  """

  _filename=None
  _threadlocal=None

  def __init__(self, filename:str):
    super().__init__()
    self._filename=filename
    self._threadlocal=local()
    self._getConnection()
    self._setupSchema()

  def _getConnection(self):
    if not hasattr(self._threadlocal,"conn"):
      self._threadlocal.conn=sqlite3.connect(self._filename)
    return self._threadlocal.conn


  def getFeeds(self) -> List[Feed]:
    """Returns all stored feeds.

    :rtype: List[Feed]
    """
    c=self._getConnection().cursor()
    query="SELECT id,sourceName,feedURL,updateInterval,title,description,websiteURL,lastRefreshed,lastChanged FROM feeds"
    c.execute(query)
    rv=[]
    for row in c:
      feed=self._feedRowToObject(row)
      feed.items=self.getItemsByFeedID(feed.id)
      rv.append(feed)
    c.close()
    return rv

  def getFeedByID(self, id:int) -> Union[Feed,None]:
    """Returns the feed with the given ID, or None if not found

    :param int id: the feed ID to look up
    :rtype: Feed or None
    """
    c=self._getConnection().cursor()
    query="SELECT id,sourceName,feedURL,updateInterval,title,description,websiteURL,lastRefreshed,lastChanged FROM feeds WHERE id=?"
    #             0  1          2       3              4     5           6          7             8
    c.execute(query,(id,))
    row=c.fetchone()
    c.close()
    if row==None:
      return None

    feed=self._feedRowToObject(row)
    feed.items=self.getItemsByFeedID(feed.id)
    return feed

  def _feedRowToObject(self,row):
    feed=Feed()
    feed.id=row[0]
    feed.sourceName=row[1]
    feed.feedURL=row[2]
    feed.updateInterval=self._sqlToTimedelta(row[3])
    feed.title=row[4]
    feed.description=row[5]
    feed.websiteURL=row[6]
    feed.lastRefreshed=self._sqlToDatetime(row[7])
    feed.lastChanged=self._sqlToDatetime(row[8])
    return feed

  def putFeed(self, feed:Feed) -> None:
    """Stores a single Feed object.

    If the feed comes with items, the items are stored as well.

    To assure thread-safety you need to get a lock by calling .acquireWriteLock() first.

    :param Feed feed: the Feed to store
    :raises AssertionError: if acquireWriteLock() wasn't called before this method
    """
    self._assertIsWriteLocked()
    conn=self._getConnection()
    c=conn.cursor()
    query=self._insertReplace(feed.id,"""%s INTO feeds
                                    (id,sourceName,feedURL,updateInterval,title,description,websiteURL,lastRefreshed,lastChanged)
                             VALUES (?, ?,         ?,      ?,             ?,    ?,          ?,         ?,            ?)""")
    #                                0, 1          2       3              4     5           6          7             8
    row=(feed.id,
         feed.sourceName,
         feed.feedURL,
         self._timedeltaToSQL(feed.updateInterval),
         feed.title,
         feed.description,
         feed.websiteURL,
         self._datetimeToSQL(feed.lastRefreshed),
         self._datetimeToSQL(feed.lastChanged))
    c.execute(query,row)
    conn.commit()
    if feed.id==None:
      feed.id=c.lastrowid

    for item in feed.items:
      item.feedID=feed.id
      self._putItem(item,c)
    conn.commit()
    c.close()

  def getItemsByFeedID(self, feed_id:int) -> List[Item]:
    """Returns all items for a given feed ID.

    :param int feed_id: the feed ID to look up items for
    :rtype: List[Item]
    """
    rv=[]
    c=self._getConnection().cursor()
    query="SELECT id,feedID,guid,title,description,itemURL,publicationDate FROM items WHERE feedID=?"
    #             0  1      2    3     4           5       6
    for row in c.execute(query,(feed_id,)):
      item=Item()
      item.id=row[0]
      item.feedID=row[1]
      item.guid=row[2]
      item.title=row[3]
      item.description=row[4]
      item.itemURL=row[5]
      item.publicationDate=self._sqlToDatetime(row[6])
      rv.append(item)
    c.close()
    return rv

  def _putItem(self, item:Item, c):
    query=self._insertReplace(item.id,"""%s INTO items (id,feedID,guid,title,description,itemURL,publicationDate)
                                                VALUES (?, ?,     ?,   ?,    ?,          ?,      ?)""")
    #                                                   0, 1      2    3     4           5       6
    row=(item.id,
         item.feedID,
         item.guid,
         item.title,
         item.description,
         item.itemURL,
         self._datetimeToSQL(item.publicationDate))
    c.execute(query,row)
    if item.id==None:
      item.id=c.lastrowid

  def _insertReplace(self,id,template:str) -> str:
    """helper method for compatibility with Python versions before 3.6.

    We need the last primary key generated/changed, this isn't implemented for the REPLACE statement until Python 3.6.
    """
    verb="INSERT"
    if id!=None:
      verb="REPLACE"
    return template%verb

  def putItem(self, item:Item) -> None:
    """Stores a single item.

    TODO: improve handling of orphaned items, probably throw exception

    To assure thread-safety you need to get a lock by calling .acquireWriteLock() first.

    :param Item item: the item to store
    :raises AssertionError: if acquireWriteLock() wasn't called before this method
    """
    self._assertIsWriteLocked()
    feed=self.getFeedByID(item.feedID)
    if feed==None:
      return
    conn=self._getConnection()
    c=conn.cursor()
    self._putItem(item,c)
    conn.commit()
    c.close()

  def _setupSchema(self):
    c=self._getConnection().cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS feeds (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   sourceName TEXT NOT NULL,
                                                   feedURL TEXT NOT NULL,
                                                   updateInterval INT,
                                                   title TEXT,
                                                   description TEXT,
                                                   websiteURL TEXT,
                                                   lastRefreshed TEXT,
                                                   lastChanged TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   feedID INT NOT NULL,
                                                   guid TEXT,
                                                   title TEXT,
                                                   description TEXT,
                                                   itemURL TEXT,
                                                   publicationDate TEXT)""")
    c.close()

  def _sqlToTimedelta(self,raw:str) -> Union[timedelta,None]:
    if raw==None:
      return None
    return timedelta(seconds=raw)

  def _timedeltaToSQL(self,obj:Union[timedelta,None]) -> Union[int,None]:
    if obj==None:
      return None
    return obj.total_seconds()

  def _sqlToDatetime(self,raw:str) -> Union[datetime,None]:
    if raw==None:
      return None
    if sys.version_info>=(3,7):
      return datetime.fromisoformat(raw) #requires Python 3.7+

    plain=datetime.strptime(raw[0:19],"%Y-%m-%d %H:%M:%S")
    microseconds=0
    tz=None
    remainder=raw[19:]
    if remainder[0]==".":
      microseconds=int(remainder[1:7])
      remainder=remainder[7:]
    if remainder!="":
      sign=None
      if remainder[0]=="+":
        sign=1
      elif remainder[0]=="-":
        sign=-1
      parts=remainder[1:].split(":")
      minutes=int(parts[0])*60
      if 1 in parts:
        minutes+=parts[0]
      tz=timezone(timedelta(seconds=sign*minutes))
    return datetime(plain.year,plain.month,plain.day,plain.hour,plain.minute,plain.second,microseconds,tz)

  def _datetimeToSQL(self,obj:Union[datetime,None]) -> Union[int,None]:
    if obj==None:
      return None
    return obj.isoformat(" ")

  def close(self):
    """Closes the (thread-local) SQLite connection.

    This method is mainly useful for multihreaded tests.
    """
    self._getConnection().close()


class TestSQLiteStorage(BaseStorageTest,unittest.TestCase):
  """Tests for the SQLiteStorage class.
  """

  def _createStorage(self):
    return SQLiteStorage(":memory:")

  def testputFeedTimeFormats(self):
    """Tests whether putFeed() correctly stores datetime-related objects.
    """
    storage=self._createStorage()

    feed=Feed()
    feed.sourceName="test"
    feed.feedURL="uri://bleh"
    feed.updateInterval=timedelta(minutes=12,seconds=37)
    feed.lastRefreshed=datetime(2018,10,6,16,17,18,192021)
    feed.lastChanged=datetime(2017,6,15,14,13,12,111009,timezone(timedelta(hours=4,minutes=30)))

    item=Item()
    item.publicationDate=datetime(2016,1,2,3,4,5,60708)
    feed.items=[item]

    storage.acquireWriteLock()
    storage.putFeed(feed)
    storage.releaseWriteLock()

    c=storage._getConnection().cursor()
    c.execute("SELECT id,updateInterval,lastRefreshed,lastChanged FROM feeds WHERE id=1")
    feed_row=c.fetchone()
    self.assertIsNotNone(feed_row,"should have found a 'feeds' row")
    self.assertEqual(12*60+37,feed_row[1],"stored feed interval should be 12m37s in seconds")
    self.assertEqual("2018-10-06 16:17:18.192021",feed_row[2],"stored lastRefreshed should be in expected date format")
    self.assertEqual("2017-06-15 14:13:12.111009+04:30",feed_row[3],"stored lastChanged should include timezone offset")

    c.execute("SELECT id,publicationDate FROM items WHERE id=1")
    item_row=c.fetchone()
    self.assertIsNotNone(item_row,"should have found an 'items' row")
    self.assertEqual("2016-01-02 03:04:05.060708",item_row[1],"stored publicationDate should be in expected date format")


  def testPutFeedWriteLock(self):
    """Checks whether putFeed() respects write locks.
    """

    def setup(storage):
      pass

    data=[Feed(title="feed 1",sourceName="test",feedURL="1"),
          Feed(title="feed 2",sourceName="test",feedURL="2"),
          Feed(title="feed 3",sourceName="test",feedURL="3")]

    def asserter(storage):
      feeds=storage.getFeeds()
      self.assertEqual(3,len(feeds))
      self.assertEqual("feed 1",feeds[0].title,"should be first either way")
      self.assertEqual("feed 2",feeds[1].title,"the earlier lock should have guaranteed this is inserted at 2nd place")
      self.assertEqual("feed 3",feeds[2].title,"delayed timer function should have added its data at the end")

    self._performWriteLockTest(setup,data,"putFeed",asserter)

  def testPutItemWriteLock(self):
    """Checks whether putItem() respects write locks.
    """

    def setup(storage):
      storage.acquireWriteLock()
      storage.putFeed(Feed(id=4,title="feed",sourceName="test",feedURL="4"))
      storage.releaseWriteLock()

    data=[Item(title="item 1",feedID=4),
          Item(title="item 2",feedID=4),
          Item(title="item 3",feedID=4)]

    def asserter(storage):
      feed=storage.getFeedByID(4)
      self.assertEqual(3,len(feed.items))
      self.assertEqual("item 1",feed.items[0].title,"should be first either way")
      self.assertEqual("item 2",feed.items[1].title,"earlier lock should have assured this is second")
      self.assertEqual("item 3",feed.items[2].title,"background thread should have been delayed")

    self._performWriteLockTest(setup,data,"putItem",asserter)

  def _performWriteLockTest(self, setup, data, putter_name, asserter):
    filename="test."+__name__+".sqlite"
    if os.path.isfile(filename):
      os.remove(filename)
    storage=SQLiteStorage(filename) #we're doing multithreaded accesses, this requires a local file
    putter=getattr(storage,putter_name)

    setup(storage)

    def later():
      storage.acquireWriteLock()
      putter(data[2])
      storage.releaseWriteLock()
    timer=Timer(1,later)
    timer.start()

    storage.acquireWriteLock()
    putter(data[0])

    # the timer calling later() will be called during this sleep() period. If the locks are working as expected the timer will
    # have to wait until our lock is released further down, only then insert its data.
    sleep(2)

    putter(data[1])
    storage.releaseWriteLock()
    # at this point the timer should get its lock and start adding data.

    timer.join()

    asserter(storage)
    storage.close()

    os.remove(filename)

