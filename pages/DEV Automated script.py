#GENERAL IMPORTS
import json
import pandas as pd
import datetime as dt
import datetime
import yfinance as yf   
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import time
import requests

import pandas as pd
import plotly.graph_objects as go

#SELENIUM IMPORTS
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from firebase_admin import db
from utils import getEnvValue

import schedule

import backend.database



def get_probabilities():
    print("Data scrapping stated")
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Chrome(options=options)

    #OPEN FIRST URL AND GET SECOND URL
    driver.get("https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html?redirect=/trading/interest-rates/countdown-to-fomc.html")
    driver.implicitly_wait(1) 

    #Switch to frame "cmeIframe-jtxelq2f"
    driver.switch_to.frame(driver.find_element(By.ID, "cmeIframe-jtxelq2f"))
    driver.implicitly_wait(1) 

    #Find the element "Form1" -> corresponds to the Quickstrike window integrated to the website
    folder = driver.find_element(By.ID, "Form1")
    driver.implicitly_wait(1)

    #Get the URL of the targetted QuickStrike table
    URL = folder.get_property('action')

    #CREATE A SECOND DRIVER TO OPEN THE RETRIEVED URL 
    driver_Click = webdriver.Firefox(options=options)
    # driver_Click = webdriver.Chrome(options=options)

    #OPEN SECOND URL
    driver_Click.get(URL)
    driver_Click.implicitly_wait(1) 
    
    #Click on the "Probabilities" component which ID is "ctl00_MainContent_ucViewControl_IntegratedFedWatchTool_lbPTree"
    folder_Click = driver_Click.find_element(By.ID, "ctl00_MainContent_ucViewControl_IntegratedFedWatchTool_lbPTree")
    folder_Click.click()
    
    #Gives an implicit wait for 5 seconds so that the QuickStrike table can load
    driver_Click.implicitly_wait(1) 

    df = pd.DataFrame()

    # st.write("Retriving data from target table")
    #Get data from the QuickStrike table and stores it in the df
    for i in range(2,15): #tr
        try:        
            current_xpath = "/html/body/form/div[3]/div[2]/div[3]/div[1]/div/div/div[1]/div/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[" + str(i) + "]"
            selected_row = driver_Click.find_element(By.XPATH, current_xpath).text
            current_df=pd.DataFrame({selected_row})
            df = pd.concat([df, current_df], ignore_index=True)
        except:
            break

    # st.write("Closing Webdriver")
    driver_Click.quit()
    driver.quit()
    df = pd.melt(df, value_vars=df.columns)
    result_df = df['value']
    # st.write(result_df)

    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d")
    backend.database.insertdata(result_df,today)
    return 0

if(not st.context.headers.get_all('API-Token') ):
    st.write('You are not authorized to access this page. Come back later.')
elif(st.context.headers.get_all('API-Token')[0] != getEnvValue('API-Token')): 
    st.write('You are not authorized to access this page. Come back later.')
else:   
    get_probabilities()