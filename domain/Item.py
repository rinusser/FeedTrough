class Item:
  """Domain class for items.
  """
  id=None              #: the internal ID, used mostly for storage, as int
  feedID=None          #: the parent feed's ID, used for storage, as int

  guid=None            #: the item's guid, as string
  title=None           #: the item's title, as string
  description=None     #: the item's description, as string
  itemURL=None         #: the item's URL, as string
  publicationDate=None #: the time this item was published, as datetime.datetime

  def __init__(self, id=None, feedID=None, title=None):
    """
    :param Union[int,None] id: optional: the item's internal ID
    :param Union[int,None] feedID: optional: the item parent feed's internal ID
    :param Union[str,None] title: optional: the item's title
    """
    self.id=id
    self.feedID=feedID
    self.title=title
