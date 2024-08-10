import os 
import json
import streamlit as st
from dotenv import load_dotenv


#Set the env variable
load_dotenv()

def getEnvValue(envVariable :str):
    
    #If the code is executed in local the os modules should be used
    # In prod the streamlit modules should be
    if(isEnvDev()):
         # Specifie cases for the private key as it's a pem key format
        if(envVariable == 'FIREBASE_PRIVATE_KEY'):
            return json.loads(os.getenv(envVariable))['privateKey']
    
        return os.getenv(envVariable)

    else:
         # Specifie cases for the private key as it's a pem key format
        if(envVariable == 'FIREBASE_PRIVATE_KEY'):
            return json.loads(st.secrets[envVariable])['privateKey']
    
        return st.secrets[envVariable]

def isEnvDev()-> bool:
    if(os.getenv('ENV') == None):
        return False
    return True

def isEnvProd() -> bool:
    return not isEnvDev()