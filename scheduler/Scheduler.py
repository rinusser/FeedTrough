from abc import ABC, abstractmethod


class Scheduler(ABC):
  storage=None
  sources=None

  def __init__(self, storage, sources):
    #TODO: type checks
    self.storage=storage
    self.sources={}
    for source in sources:
      self.sources[source.name]=source
      print("got source: %s"%source.name)

  @abstractmethod
  def run(self):
    pass

