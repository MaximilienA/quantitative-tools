import datetime
import time

import backend.database

while True:
        now = datetime.datetime.now()
        # now = now.replace(hour=now.houdr + 1)
        formatted_time = now.strftime("%H:%M:%S")

        backend.database.insertdata(str(formatted_time))
        
        time.sleep(10)