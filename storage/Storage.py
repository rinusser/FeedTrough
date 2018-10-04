from abc import ABC, abstractmethod
from typing import List,Union

from domain import *


class Storage(ABC):
  """Abstract base class for data storage.
  """

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
