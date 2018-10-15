import argparse
import logging


actions=["server"]


class Configuration:
  """Data class for runner configuration.
  """
  action=None            #: the action to perform (as str)

  runTime=60             #: the application lifetime, in seconds (as int or float)
  logLevel=logging.INFO  #: the default log level
  serverPort=58000       #: the TCP port to listen on


def parse_cli_arguments() -> Configuration:
  """Parses command-line arguments into a Configuration object.

  This function will not return if the help screen was requested.

  :return Configuration: the parsed configuration
  """
  parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  log_levels=["critical","error","warning","info","debug","off"]
  parser.add_argument("--port",dest="serverPort",type=int,default=Configuration.serverPort,help="the server port to listen on")
  parser.add_argument("--log-level",dest="logLevel",choices=log_levels,default="info",help="the default log level")
  parser.add_argument("--runtime",dest="runTime",type=int,default=Configuration.runTime,help="the application lifetime in seconds, 0 to keep running indefinitely")
  parser.add_argument("action",metavar="action",default=actions[0],choices=actions,nargs="?",help="the application action to perform")
  args=parser.parse_args()

  config=Configuration()
  config.serverPort=args.serverPort
  config.logLevel=_parseLogLevel(args.logLevel)
  config.runTime=args.runTime

  return config


def _parseLogLevel(raw:str):
  map={"critical":logging.CRITICAL,
       "error":   logging.ERROR,
       "warning": logging.WARNING,
       "info":    logging.INFO,
       "debug":   logging.DEBUG,
       "off":     logging.NOTSET}
  key=raw.lower()
  if not key in map:
    raise ValueError("invalid log level '%s'"%raw)
  return map[key]

