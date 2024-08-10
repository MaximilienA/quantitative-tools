import os 
import json
from dotenv import load_dotenv

def getEnvValue(envVariable :str):
    load_dotenv()
    if(envVariable == 'FIREBASE_PRIVATE_KEY'):
        return json.loads(os.getenv(envVariable))['privateKey']
    return os.getenv(envVariable)