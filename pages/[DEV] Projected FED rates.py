#GENERAL IMPORTS
import pandas as pd
import datetime as dt
import datetime
import yfinance as yf   
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import time

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

import schedule

import backend.database

st.write("# Developpement page")

# ===== FUNCTION THAT OPEN THE BASE WEBPAGE IN A SIMULATED HEADLESS FIREFOX WINDOW AND RETURNS THE VALUES IN THE TABLE =====
    # Parameters : no parameters
    # Return : dataframe of the values of the table (header and the 8 rows)
    # Return example :   
    # scrapped_data_from_website_df 
    # 0    MEETING DATE 300-325 325-350 350-375 375-400 4...
    # 1    31/01/2024 0,0% 0,0% 0,0% 0,0% 15,5% 84,5% 0,0...
    # 2    20/03/2024 0,0% 0,0% 0,0% 0,0% 0,0% 0,0% 0,0% ...
    # 3    01/05/2024 0,0% 0,0% 0,0% 0,0% 0,0% 0,0% 0,0% ...
    # 4    12/06/2024 0,0% 0,0% 0,0% 0,0% 2,6% 23,7% 56,0...
    # 5    31/07/2024 0,0% 0,0% 0,0% 2,2% 20,9% 51,7% 21,...
    # 6    18/09/2024 0,0% 0,0% 2,1% 19,9% 50,2% 23,2% 4,...
    # 7    07/11/2024 0,0% 0,0% 1,4% 13,9% 40,0% 32,3% 10...
    # 8    18/12/2024 1,1% 11,3% 34,4% 33,9% 15,2% 3,5% 0...
def get_probabilities():
    options = Options()
    options.add_argument('--headless')

    st.write("Creating Web driver")
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Chrome(options=options)

    st.write("Opening browser")
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

    st.write("Retriving data from target table")
    #Get data from the QuickStrike table and stores it in the df
    for i in range(2,15): #tr
        try:        
            current_xpath = "/html/body/form/div[3]/div[2]/div[3]/div[1]/div/div/div[1]/div/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[" + str(i) + "]"
            selected_row = driver_Click.find_element(By.XPATH, current_xpath).text
            current_df=pd.DataFrame({selected_row})
            df = pd.concat([df, current_df], ignore_index=True)
        except:
            break

    st.write("Closing Webdriver")
    driver_Click.quit()
    driver.quit()
    df = pd.melt(df, value_vars=df.columns)
    result_df = df['value']

    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d")
    st.write("Data scrapping ended")
    st.write("Uploading data to database")
    backend.database.insertdata(result_df,today)
    return 0



# Run the scheduler indefinitely
def startBackgroundScrapping():
    # while True:
    # schedule.run_pending()
    #     time.sleep(1)
    # schedule.every(1).day.do(get_probabilities)
    get_probabilities()

def my_function():
    st.write("Button clicked!") 

if st.button("Start data scrapping and upload data to database"):
    startBackgroundScrapping()