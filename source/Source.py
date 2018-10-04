from abc import ABC, abstractmethod

from domain import *


class Source(ABC):
  """Abstract base class for data sources.

  Implementations are expected to read/aggregate data from whatever upstream source they represent.

  Potential sources may be RSS feeds, scraped web content, local log files, etc.
  """

  @property
  @abstractmethod
  def name(self) -> str:
    """abstract getter: this method should return the source's (unique) name

    :rtype: str
    """
    pass

  @abstractmethod
  def updateFeed(self, feed:Feed) -> None:
    """abstract: this should update feed data from its source, e.g. an upstream RSS feed

    :param Feed feed: the feed to update
    """
    pass

