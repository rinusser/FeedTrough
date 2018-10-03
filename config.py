import logger

log=logger.get_logger(__name__)

sources=[
]

try:
  f=open("sources.txt","r")
  for line in f:
    if line.strip()=="" or line[0]=="#":
      continue
    type,url=line.split(":",maxsplit=1)
    sources.append((type.strip(),url.strip()))
  f.close()
except FileNotFoundError:
  log.warn("no sources.txt found")

