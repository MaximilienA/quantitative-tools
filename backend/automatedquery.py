import datetime
import time
import backend.database

def lauchautomatedquery():
    while (i<=10):
            now = datetime.datetime.now()
            # now = now.replace(hour=now.houdr + 1)
            formatted_time = now.strftime("%H:%M:%S")

            backend.database.insertdata(str(formatted_time))
            
            time.sleep(5)
            i++
