from runner import *
from storage import *


if __name__=="__main__":
  configuration=parse_cli_arguments()
  runner=Runner(storage=SQLiteStorage("feeds.sqlite"),configuration=configuration)
  runner.run()

