from abc import ABC, abstractmethod
from threading import Lock
from typing import List,Union

from domain import *


class Storage(ABC):
  """Abstract base class for data storage.

  Storage implementations may be thread safe - check the actual implementations' documentation on whether they are. For this
  purpose, you should acquire/release a write lock before/after performing write accesses. Thread-safe storage implementations
  should throw AssertionErrors if you attempt to write data without locks.

  Unless you're customizing the write lock mechanism, derived classes should invoke this class's __init__() method.
  """

  _writeLock=None

  def __init__(self):
    self._writeLock=Lock()

  def acquireWriteLock(self):
    """Gets a write lock for the storage.

    This method call will block if someone else got a lock first.

    Locks need to be released with .releaseWriteLock().
    """
    return self._writeLock.acquire()

  def releaseWriteLock(self):
    """Releases a write lock.
    """
    return self._writeLock.release()

  def isWriteLocked(self):
    """Checks whether the storage is currently write-locked.

    :return bool: whether a write lock is in place
    """
    was_unlocked=self._writeLock.acquire(blocking=False)
    if was_unlocked:
      self._writeLock.release()
    return not was_unlocked

  def _assertIsWriteLocked(self):
    assert self.isWriteLocked()

  @abstractmethod
  def getFeeds(self) -> List[Feed]:
    """abstract: this should return a list of all feeds

    :rtype: List[Feed]
    """
    pass

  @abstractmethod
  def getFeedByID(self, id:int) -> Union[Feed,None]:
    """abstract: this should return the feed with the given ID, or None if not found

    :param int id: the feed ID to look up
    :rtype: Feed or None
    """
    pass

  @abstractmethod
  def putFeed(self, feed:Feed) -> None:
    """abstract: this should store a feed

    If the feed comes with items, the items should be stored as well.

    :param Feed feed: the Feed to store
    """
    pass

  @abstractmethod
  def getItemsByFeedID(self, feed_id:int) -> List[Item]:
    """abstract: this should return all items for a given feed ID

    :param int feed_id: the feed ID to look up items for
    :rtype: List[Item]
    """
    pass

  @abstractmethod
  def putItem(self, item:Item) -> None:
    """abstract: this should store an item

    If the item doesn't belong to a known feed, the item should be discarded.

    :param Item item: the item to store
    """
    pass
