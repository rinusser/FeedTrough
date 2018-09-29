from abc import ABC, abstractmethod
from typing import List

from source import Source
from storage import Storage


class Scheduler(ABC):
  storage=None
  sources=None

  def __init__(self, storage:Storage, sources:List[Source]):
    self.storage=storage
    self.sources={}
    for source in sources:
      self.sources[source.name]=source
#      print("got source: %s"%source.name)

  @abstractmethod
  def run(self) -> None:
    pass

