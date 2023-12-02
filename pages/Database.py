import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
import streamlit as st

cred = credentials.Certificate('quantitativetoolsdatabase-90b51ea9a1ca.json')
firebase_admin.initialize_app(cred, {"databaseURL" : "https://quantitativetoolsdatabase-default-rtdb.europe-west1.firebasedatabase.app/"})

ref = db.reference("/")
st.write(ref.get()) 