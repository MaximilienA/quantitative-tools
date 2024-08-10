import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
import streamlit as st
import datetime
from utils import getEnvValue
import pandas as pd

print(getEnvValue('FIREBASE_CLIENT_MAIL'))
cred = credentials.Certificate( {
    "project_id": getEnvValue('FIREBASE_PROJECT_ID'),
    "private_key": getEnvValue('FIREBASE_PRIVATE_KEY'),
    "client_email": getEnvValue('FIREBASE_CLIENT_MAIL'),
    "type": "service_account",
    "token_uri": "https://oauth2.googleapis.com/token",
})

    #'backend/quantitativetoolsdatabase-90b51ea9a1ca.json')
if not firebase_admin._apps:
    default_app = firebase_admin.initialize_app(cred, {"databaseURL" : "https://quantitativetoolsdatabase-default-rtdb.europe-west1.firebasedatabase.app/"})

def insertdatatest(scrapped_data, date):
    for i in range(1,2):
        # db.reference("/Test").push().set(data)
        database_path = "/scrapped_FED_rates/" + str(date)

        ref = db.reference(database_path)
        ref.set(scrapped_data)
        # ref.set(scrapped_data.to_dict())

def insertdata(scrapped_data, date):
    for i in range(1,2):
        # db.reference("/Test").push().set(data)
        database_path = "/scrapped_FED_rates/" + str(date)

        ref = db.reference(database_path)
        # ref.set(scrapped_data)
        dataDict = scrapped_data.to_dict()
        # st.write(dataDict)
        ref.set(dataDict)

today = datetime.date.today()
today = today.strftime("%Y-%m-%d")

# def get(data)

# st.write(ref.get()) 