from abc import ABC, abstractmethod
from typing import List,Union

from domain import *


class Storage(ABC):
  @abstractmethod
  def getFeeds(self) -> List[Feed]:
    pass

  @abstractmethod
  def getFeedByID(self, id:int) -> Union[Feed,None]:
    pass

  @abstractmethod
  def putFeed(self, feed:Feed) -> None:
    pass

  @abstractmethod
  def getItemsByFeedID(self, feed_id:int) -> List[Item]:
    pass

  @abstractmethod
  def putItem(self, item:Item) -> None:
    pass
