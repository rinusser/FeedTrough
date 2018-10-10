from runner import *
from storage import *


if __name__=="__main__":
  runner=Runner(SQLiteStorage("feeds.sqlite"))
  runner.run()

