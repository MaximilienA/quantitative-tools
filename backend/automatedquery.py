import datetime
import time
import backend.database
import pandas as pd

def lauchautomatedquery():
    i = 0
    while i<5:
        now = datetime.datetime.now()
        now = now.replace(hour=now.hour + 1)
        formatted_time = now.strftime("%H:%M:%S")

        #backend.database.insertdata(str(formatted_time))
        
        data = {'name': ['Alice', 'Bob', 'Charlie'], 'age': [32, 54, 27], 'city': ['New York', 'Chicago', 'Los Angeles']}
        df = pd.DataFrame(data)
        json_data = df.to_json(orient='records')
        backend.database.insertdata(json_data)

        time.sleep(3)
        i += 1
