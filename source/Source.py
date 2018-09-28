from abc import ABC, abstractmethod


class Source(ABC):
  @property
  @abstractmethod
  def name(self):
    pass

  @abstractmethod
  def updateFeed(self, feed):
    pass

