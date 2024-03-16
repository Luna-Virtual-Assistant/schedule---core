import time
from datetime import datetime, timedelta
from pytz import timezone

print(datetime.now(timezone("UTC")) +
      timedelta(minutes=2))
