from abc import ABC, abstractmethod

class Storage(ABC):
  @abstractmethod
  def getFeeds(self):
    pass

  @abstractmethod
  def getFeedByID(self, id):
    pass

  @abstractmethod
  def putFeed(self, feed):
    pass

  @abstractmethod
  def getItemsByFeedID(self, feed_id):
    pass

  @abstractmethod
  def putItem(self, item):
    pass

