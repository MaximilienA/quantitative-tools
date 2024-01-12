#GENERAL IMPORTS
import pandas as pd
import datetime as dt
from datetime import timedelta 
from datetime import date
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

import backend.database


# def run():
#     st.set_page_config(page_title="Data scrapping : projected FED rate",)

with st.spinner('Scrapping data...'):
    time.sleep(60)

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

    #Get data from the QuickStrike table and stores it in the df
    for i in [2, 3, 4, 5, 6, 7, 8, 9, 10]: #tr
        
        current_xpath = "/html/body/form/div[3]/div[2]/div[3]/div[1]/div/div/div[1]/div/div[3]/div[3]/div/div/table[2]/tbody/tr[" + str(i) + "]"

        selected_row = driver_Click.find_element(By.XPATH, current_xpath).text

        current_df=pd.DataFrame({selected_row})

        df = pd.concat([df, current_df], ignore_index=True)
        # df.iloc[i, j] = selected_row
            
    # df = df.set_index(['row', 'col'])   

    # current_df=pd.DataFrame({selected_row})
    
    # df.append(current_df, ignore_index=True)

    # df = pd.concat([df, current_df], ignore_index=True)
    driver_Click.quit()
    driver.quit()
    df = pd.melt(df, value_vars=df.columns)
    result_df = df['value']
    return result_df

# df_scrapped_data_from_website = get_probabilities()

# df_buffer_scrapped_data_from_website = df_scrapped_data_from_website
# df_buffer_scrapped_data_from_website

# ===== FUNCTION THAT TAKES A probabilities_scrapped_raw STRING IN PARAMETER AND RETURNS THE DATE OF THIS STRING ===== 
    #Parameters : probabilities_scrapped_raw : the probabilities_scrapped_raw string
    #Return example : 13/12/2023
def dataSpliterDate(probabilities_scrapped_raw): # Split the data into date and percentage
    date_probabilities = probabilities_scrapped_raw[0].split(" ")
    # Extract the date
    returned_date = date_probabilities[0]
    return returned_date

# ===== FUNCTION TO TRANSFORM ONE LINE OF THE probabilities_scrapped_raw string in a transposed dataframe ===== 
    #Parameters : 
        # - dataheader : the data_headers_raw string : "MEETING DATE 325-350 350-375 375-400 400-425 4..."
        # - data_probabilities : the data_probabilities_raw string :"1/31/2024 0.0% 0.0% 0.0% 0.0% 6.7% 93.3%"
        # - index : a binary index to know if the data is the first one and to add two 0 to counter the default of the initial targetted QuickStrike table
    #Return : the sliced dataframe corresponding to a specific date
    #Return example : 
    # Rates Percentage
    # 0  350-375       0,0%
    # 1  375-400       0,0%
    # 2  400-425       0,0%
    # 3  425-450       0,0%
    # 4  450-475       0,0%
    # 5  475-500      95,5%
    # 6  500-525       4,5%
    # 7  525-550       0,0%
    # 8  550-575          0
    # 9  575-600          0
def dataSlicer(data_headers_raw, data_probabilities_raw, index):
    #Split the data into date and percentages
    data_headers_clean = data_headers_raw[0].split(" ")
    date_percentages_clean = data_probabilities_raw[0].split(" ")

    #Extract the date and percentages
    # date = date_percentages_clean[0]
    percentages = date_percentages_clean[1:]

    #Adjust the lenght of the first probabilities row (next date's probabilities)  to the lenght of the header row : "MEETING DATE 325-350 350-375 375-400 400-425 4..."
    while (len(percentages) != len(data_headers_clean[1:])):
        percentages.insert(0, "0,0%")  
    
    #Create a DataFrame
    df = pd.DataFrame([percentages], columns=data_headers_clean[1:])
    df = df.T
    df = df.reset_index()
    df.columns = ['Rates', 'Percentage']
    return df

def dfRatesMerger():

    scrapped_data_from_website_df  = get_probabilities()

    Rates_df = pd.DataFrame({"Rates": ["0-25",	"25-50",	"50-75",	"75-100",	"100-125",	"125-150",	"150-175",	"175-200",	"200-225",	"225-250",	"250-275",	"275-300",	"300-325",	"325-350",	"350-375",	"375-400",	"400-425",	"425-450",	"450-475",	"475-500",	"500-525",	"525-550",	"550-575",	"575-600",	"600-625",	"625-650",	"650-675",	"675-700",	"700-725",	"725-750",	"750-775",	"775-800",	"800-825",	"825-850",	"850-875",	"875-900",	"900-925",	"925-950",	"950-975",	"975-1000"]})

    #For each meeting date...
    for i in [8, 7, 6, 5, 4, 3, 2, 1]:

        #Get the raw header
        header_scrapped_raw = scrapped_data_from_website_df.iloc[0]
        #Get the raw probabilities
        probabilities_scrapped_raw = scrapped_data_from_website_df.iloc[i] 

        #Delete the "MEETING" frome the header of the retrieve table
        header_scrapped_raw = header_scrapped_raw[8:]

        #Retransform the raw probabilities in a clean dataframe
        transformed_dateframe_of_specific_meeting_date = dataSlicer([header_scrapped_raw], [probabilities_scrapped_raw], i) #for loop on 1
        Date_of_specific_meeting_date = dataSpliterDate([probabilities_scrapped_raw])

        #Merge the clean dataframe with the default rate interval
        Rates_df=pd.merge(transformed_dateframe_of_specific_meeting_date,Rates_df, how='right', on='Rates')

        #Format final table
        Rates_df.rename(columns={'Percentage': Date_of_specific_meeting_date}, inplace=True)
        Rates_df = Rates_df.fillna("0,0%")

    Rates_df.replace('0,0%', 0, inplace=True)
    Rates_df = (Rates_df.loc[(Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1) | (Rates_df[[Rates_df.columns[0]]]!= 0).all(axis=1)]).T

    Rates_df.columns = Rates_df.iloc[0]
    Rates_df = Rates_df.iloc[1:]         
    return Rates_df

final_df = dfRatesMerger()

final_scrapped_df = final_df

dataframe_from_database = final_scrapped_df

#Map function to replace European percentage type values in decimal type values : the percentage '65.0%' will be converted to '68.5 and '0,00' will be converted to '0'
def convert_percentage(x):
    if isinstance(x, str):
        value = (x.replace('%', ''))     
        # value = value.replace(',', '.')
        return value
    else:
        return x
        
#Function to convert the range value in column names to a single rate : 475-500' will be converted to '5'
def convertRateRanges(dataframe_from_database):
    #Define the range values
    ranges = dataframe_from_database.columns

    #Convert each range to its upper rate : the rate range '475-500' will be converted to '5'
    midpoints = []
    for range_str in ranges:
        # Split the range string into its two values
        values = range_str.split("-")
        start_value = int(values[0])
        end_value = int(values[1])

        # Calculate the midpoint
        midpoint = end_value /100

        # Add the midpoint to the list of midpoints
        midpoints.append(midpoint)

    # print(midpoints, "\n")

    dataframe_from_database.columns = midpoints

    dataframe_from_database = dataframe_from_database.T

    return dataframe_from_database

def transformReworkedDataframeToDisplayableDataframe(dataframe_from_database):
    #Replace European percentage type values in decimal type values 
    dataframe_from_database = dataframe_from_database.map(convert_percentage)

    #Convert all percentages probabilities to float64
    for col in dataframe_from_database.columns:
        if pd.api.types.is_numeric_dtype(dataframe_from_database[col]):
            continue
        try:
            dataframe_from_database[col] = pd.to_numeric(dataframe_from_database[col])
        except:
            pass

    #Convert the range value in column names to a single rate :
    dataframe_from_database = convertRateRanges(dataframe_from_database)

    selected_columns = [dataframe_from_database.columns[0], dataframe_from_database.columns[1], dataframe_from_database.columns[2], dataframe_from_database.columns[3], dataframe_from_database.columns[4], dataframe_from_database.columns[5], dataframe_from_database.columns[6], dataframe_from_database.columns[7]]

    print("selected_columns", selected_columns, "\n")

    max_values_probability_rate = dataframe_from_database[selected_columns].idxmax(axis=0)

    print("max_values_indices", max_values_probability_rate, "\n")

    max_probability = dataframe_from_database.max(axis=0)

    print("max_values", max_probability, "\n")

    # # Print the indices of the maximum values in each row
    # print("max_values_indices", max_values_indices)

    df_to_display_in_graph = max_values_probability_rate.to_frame()
    df_to_display_in_graph['Probabilities']=(max_probability)
    # Print the DataFrame
    df_to_display_in_graph.columns = ['Upper range rate','Probabilities']
    return df_to_display_in_graph

df_to_display_in_graph = transformReworkedDataframeToDisplayableDataframe(dataframe_from_database)

# df_to_display_in_graph

# ===== PYPLOT =====
# Create the line graph
plt.figure(figsize=(16, 6))
plt.plot(df_to_display_in_graph.index, df_to_display_in_graph['Upper range rate'], marker='o', linestyle='-')
plt.xlabel('Date')
plt.ylabel('Upper range rate')
plt.title('Projected rates')
plt.grid(True)

# Scale Y axis by 0.25
def make_increment(start, end, num_steps):
    return [start + i * (end - start) / (num_steps - 1) for i in range(num_steps)]

max_value = df_to_display_in_graph['Upper range rate'].max()
min_value = df_to_display_in_graph['Upper range rate'].min()
increment_values = make_increment(max_value+0.25, min_value-0.25, int((max_value-min_value)/0.25)+3)
plt.gca().set_yticks(increment_values)

plt.show()

st.pyplot(plt)

    # ===== DATABASE =====
    # now = datetime.datetime.now()
    # now = now.replace(hour=now.hour + 1)
    # formatted_time = now.strftime("%H:%M:%S")

    # json_data = final_scrapped_df.to_json(orient='table', compression='dict')
    # json_data = str(formatted_time) + " " + json_data
    # # Convert JSON object to a list
    # data_list = list(json_data.items())

    # # Create a new key-value pair to insert
    # new_data = ('Date', formatted_time)

    # # Insert the new data at the first position
    # data_list.insert(0, new_data)

    # # Convert the list back to a JSON object
    # data = dict(data_list)

    # print(data)

    # st.write(json_data)
    # st.write(type(json_data))
    
    # st.write(final_scrapped_df)

    # backend.database.insertdata(json_data)

    #streamlit run "C:\Users\pluto\Desktop\Investissement\Python\Test courbe taux futures\SeleniumLocal.py"
    # return json_data

