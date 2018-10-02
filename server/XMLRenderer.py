from PyRSS2Gen import *
from datetime import datetime

from domain import *


class XMLRenderer:
  def renderFeed(self, feed:Feed) -> str:
    items=[]
    for item in feed.items:
      items.append(RSSItem(title=item.title,
                           link=item.itemURL,
                           description=item.description,
                           guid=item.guid,
                           pubDate=item.publicationDate))
    rss=RSS2(title=feed.title,
             link=feed.websiteURL,
             description=feed.description,
             lastBuildDate=feed.lastRefreshed,
             items=items)
    return rss.to_xml()
