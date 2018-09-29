from abc import ABC, abstractmethod

from domain import *


class Source(ABC):
  @property
  @abstractmethod
  def name(self) -> str:
    pass

  @abstractmethod
  def updateFeed(self, feed:Feed) -> None:
    pass

