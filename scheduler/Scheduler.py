from abc import ABC, abstractmethod
import threading
from typing import List

from source import Source
from storage import Storage


class Scheduler(threading.Thread, ABC):
  """Abstract base class for schedulers.
  """

  _storage=None
  _sources=None

  def __init__(self, storage:Storage, sources:List[Source]):
    """
    :param Storage storage: where to read/write feed data from/to
    :param List[Source] sources: the sources to use for feed updates
    """
    super().__init__(daemon=True)
    self._storage=storage
    self._sources={}
    for source in sources:
      self._sources[source.name]=source

  @abstractmethod
  def run(self) -> None:
    """abstract: this method should contain the scheduler's implementation.
    """
    pass

