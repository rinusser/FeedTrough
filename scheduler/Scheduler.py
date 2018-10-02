from abc import ABC, abstractmethod
import threading
from typing import List

from source import Source
from storage import Storage


class Scheduler(threading.Thread, ABC):
  storage=None
  sources=None

  def __init__(self, storage:Storage, sources:List[Source]):
    super().__init__(daemon=True)
    self.storage=storage
    self.sources={}
    for source in sources:
      self.sources[source.name]=source

  @abstractmethod
  def run(self) -> None:
    pass

