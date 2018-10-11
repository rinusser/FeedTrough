from datetime import datetime, timedelta
import logging
from time import sleep
from uuid import uuid4
import unittest

from domain import *
import logger
from scheduler import *
from server import *
from source import *
from debug import *
import config


log=logger.get_logger(__name__)


class Runner:
  """This class sets/instantiates all values, objects, threads etc. to actually run the application.
  """

  _sources=None
  _storage=None
  _feedSpecs=[]
  _runTime=60


  def __init__(self, storage:Storage, sources:Union[List[Source],None]=None, feedSpecs=None, runTime:int=60):
    """
    :param Storage storage: the storage backend to use
    :param Union[List[Source],None] sources: a list of sources for reading feeds (defaul: all built-in)
    :param Union[List,None] feedSpecs: optional: the feed parameters to use (default: config.sources)
    :param int runTime: optional: how long the application should run, in seconds (as int or float)
    """
    self._storage=storage

    if sources!=None:
      self._sources=sources
    else:
      self._sources=[DummySource(),FeedSource()]

    if feedSpecs!=None:
      self._feedSpecs=feedSpecs
    else:
      self._feedSpecs=config.sources

    self._runTime=runTime


  def run(self):
    """Starts the application.
    """
    logger.register_handler(logging.INFO)

    self._compileFeeds()

    scheduler=StandaloneScheduler(self._storage,self._sources)
    scheduler.start()

    server=FeedServer(self._storage)
    server.start()

    try:
      sleep(self._runTime)
    except KeyboardInterrupt:
      pass

    log.info("exiting application")


  def _compileFeeds(self):
    stored_feeds=self._storage.getFeeds()
    handled_specs=[]
    for feed in stored_feeds:
      spec=(feed.sourceName,feed.feedURL)
      active=spec in self._feedSpecs
      handled_specs.append(spec)
      logstr="feed type=%s, url=%s:"%spec
      if active:
        if feed.updateInterval!=None:
          log.debug("%s keeping active",logstr)
          continue
        else:
          log.debug("%s reactivating",logstr)
          feed.updateInterval=timedelta(minutes=60)
      else:
        if feed.updateInterval!=None:
          log.debug("%s deactivating",logstr)
          feed.updateInterval=None
        else:
          log.debug("%s keeping inactive",logstr)
          continue
      self._storage.putFeed(feed)

    unhandled_specs=set(self._feedSpecs)-set(handled_specs)
    for type,url in unhandled_specs:
      log.info("got new source: type %s, url %s",type,url)
      feed=Feed(sourceName=type,feedURL=url)
      feed.updateInterval=timedelta(minutes=5)
      self._storage.putFeed(feed)


class TestRunner(unittest.TestCase):
  """Tests for the Runner class.
  """

  def testCompileFeeds(self):
    """Checks whether _compileFeeds() correctly merges feeds from storage and sources.txt.
    """
    storage=SQLiteStorage(":memory:")
    interval=timedelta(seconds=60)
    storage.putFeed(Feed(id=1,sourceName="dummy",feedURL="f1",updateInterval=interval))
    storage.putFeed(Feed(id=2,sourceName="dummy",feedURL="f2",updateInterval=None))
    storage.putFeed(Feed(id=3,sourceName="other",feedURL="f3",updateInterval=interval))
    sources=[DummySource()]
    feed_specs=[("dummy","f2"),("dummy","f3")]

    runner=Runner(storage,sources,feed_specs)
    runner._compileFeeds()

    stored_feeds=storage.getFeeds()
    self.assertEqual(4,len(stored_feeds),"number of feeds: 1 deactivated + 1 overwritten + 1 kept + 1 added")

    #                feed,           id,type,   url, active
    self._assertFeed(stored_feeds[0],1, "dummy","f1",False)
    self._assertFeed(stored_feeds[1],2, "dummy","f2",True)
    self._assertFeed(stored_feeds[2],3, "other","f3",False)
    self._assertFeed(stored_feeds[3],4, "dummy","f3",True)

  def _assertFeed(self, feed:Feed, id:int, type:str, url:str, active:bool):
    self.assertEqual(id,feed.id)
    self.assertEqual(type,feed.sourceName)
    self.assertEqual(url,feed.feedURL)
    self.assertEqual(active,feed.updateInterval!=None)
