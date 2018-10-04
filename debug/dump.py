from typing import List

from domain import *


def dump_item(item:Item, details:bool=True):
  """Prints Item data to stdout.

  :param Item item: the item to dump
  :param bool details: whether to include item details (default: True)
  """
  print("  item id=%s"%item.id)
  if details:
    print("    feedID=%d"%item.feedID)
    print("    guid=%s"%item.guid)
  print("    title=%s"%item.title)
  if details:
    print("    description=%s"%item.description)
    print("    itemURL=%s"%item.itemURL)
    print("    publicationDate=%s"%item.publicationDate)

def dump_feed(feed:Feed, hint=None, details:bool=True):
  """Prints Feed data to stdout.

  :param Feed feed: the feed to dump
  :param str hint: a feed description to include (default: None)
  :param bool details: whether to include feed details (default: True)
  """
  hint_text=""
  if hint!=None:
    hint_text=" (%s)"%hint
  print("feed id=%d%s"%(feed.id,hint_text))
  if details:
    print("  feedURL=%s"%feed.feedURL)
    print("  updateInterval=%s"%feed.updateInterval)
  print("  title=%s"%feed.title)
  if details:
    print("  description=%s"%feed.description)
    print("  websiteURL=%s"%feed.websiteURL)
    print("  lastRefreshed=%s"%feed.lastRefreshed)
    print("  lastChanged=%s"%feed.lastChanged)
  for item in feed.items:
    dump_item(item,details=details)

def dump_feeds(feeds:List[Feed],details:bool=True):
  """Prints multiple Feeds' data to stdout.

  :param List[Feed] feed: the feeds to dump
  :param bool details: whether to include feed details (default: True)
  """
  for feed in feeds:
    dump_feed(feed,details=details)

