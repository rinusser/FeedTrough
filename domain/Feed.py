class Feed:
  """Domain class for feeds.
  """
  id=None             #: the internal ID, used mostly for persistence, as int

  sourceName=None     #: the source's name, used by schedulers to decide which source to update feed from, as string
  feedURL=None        #: the upstream URL, used by source to decide where to read feed from (e.g. the RSS URL), as string
  updateInterval=None #: time between reads from upstream, as datetime.timedelta. If set to None the feed won't be updated.

  title=None          #: the feed's title, as string
  description=None    #: the feed's description, as string
  websiteURL=None     #: the website URL this feed represents, as string

  lastRefreshed=None  #: the last time this feed was read from the source, as datetime.datetime
  lastChanged=None    #: the last time this feed changed, as datetime.datetime

  items=[]            #: items in this feed, as array of domain.Item objects


  def __init__(self, id=None, sourceName=None, feedURL=None, updateInterval=None, title=None):
    """
    :param Union[int,None] id: optional: the feed's internal ID
    :param Union[str,None] sourceName: the feed source's name (e.g. "feed" for FeedSource)
    :param Union[str,None] feedURL: the feed URL - exact meaning depends on source type
    :param Union[datetime.timedelta,None] updateInterval: how often the feed should be updated
    :param Union[str,None] title: the feed's title
    """
    self.id=id
    self.sourceName=sourceName
    self.feedURL=feedURL
    self.updateInterval=updateInterval
    self.title=title
    self.items=[]

