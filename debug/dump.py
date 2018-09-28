def dump_item(item, details=True):
  print("  item id=%d"%item.id)
  if details:
    print("    feedID=%d"%item.feedID)
    print("    guid=%s"%item.guid)
  print("    title=%s"%item.title)
  if details:
    print("    description=%s"%item.description)
    print("    itemURL=%s"%item.itemURL)
    print("    publicationDate=%s"%item.publicationDate)

def dump_feed(feed, hint=None, details=True):
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

def dump_feeds(feeds,details=True):
  for feed in feeds:
    dump_feed(feed,details=details)

