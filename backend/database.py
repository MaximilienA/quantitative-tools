import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
import streamlit as st
import datetime
import utils
import pandas as pd

cred = credentials.Certificate( {
    "project_id": utils.getEnvValue('FIREBASE_PROJECT_ID'),
    "private_key": utils.getEnvValue('FIREBASE_PRIVATE_KEY'),
    "client_email": utils.getEnvValue('FIREBASE_CLIENT_MAIL'),
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

def query_data_by_date(input_date):
    database_path = "/scrapped_FED_rates/" + str(input_date)
    print(database_path)
    ref = db.reference(database_path)
    result = ref.get()
    result = pd.Series(result)
    return result 


def get_all_dates():
    dates = []
    database_path = "/scrapped_FED_rates/"
    ref = db.reference(database_path)
    data = ref.get()
    # for value in data.items():
        # dates.append(value['date'])
    return data



# def get(data)

# st.write(ref.get())