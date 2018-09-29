class Feed:
  id=None
  sourceName=None
  feedURL=None        #upstream feed URL
  updateInterval=None #time between reads from upstream, as datetime.timedelta

  title=None
  description=None
  websiteURL=None     #rss.link

  lastRefreshed=None  #rss.pubDate, as datetime.datetime
  lastChanged=None    #rss.lastBuildDate, as datetime.datetime

  items=[]


  def __init__(self):
    self.items=[]

