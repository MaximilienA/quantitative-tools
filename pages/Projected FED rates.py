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

from firebase_admin import db

import schedule

import backend.database

st.write("# Projected FED rates")

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

    # st.write("Creating Web driver")
    driver = webdriver.Firefox(options=options)
    # driver = webdriver.Chrome(options=options)

    # st.write("Opening browser")
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

# def my_function():
#     st.write("Button clicked!") 

# if st.button("Start data scrapping and upload data to database"):
#     startBackgroundScrapping()


        
# st.write(backend.database.query_data_by_date('2024-08-10'))

dates_list = backend.database.get_all_dates()

dict1 = (list(dates_list.keys()))
dict2 = (list(dates_list.keys()))

date1 = st.selectbox(
    'Choose first date',
    list(dict1),  # Utiliser les clés du dictionnaire comme options
    key='selectbox_date1'
)

date2 = st.selectbox(
    'Choose second date',
    list(dict2),  # Utiliser les clés du dictionnaire comme options
        key='selectbox_date2'
)

# Get collection names
# collection_names = get_all_collection_names()

# Display collection names in a list format
# st.write("### Collections in Firebase Firestore:")
# st.write(collection_names)

    
# today = datetime.date.today()
# today = today.strftime("%Y-%m-%d")

# st.write(type(backend.database.query_data_by_date(date1)))
dataframe_from_database1 = backend.database.query_data_by_date(date1)
dataframe_from_database2 = backend.database.query_data_by_date(date2)

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

def dfRatesMerger(dataframe_from_database1):
    now = datetime.datetime.now()
    print("Starting data scrapping at : ", now.strftime("%H:%M:%S"))
    # st.write("Starting data scrapping")
    scrapped_data_from_website_df  = dataframe_from_database1
    numberOfMeetingDates = (len(scrapped_data_from_website_df)-1)
    now = datetime.datetime.now()
    print("Ending data scrapping at : ", now.strftime("%H:%M:%S"))
    # st.write("Data scrapping ended")
    # st.write("Data ready for cleaning")
    # st.write("Data ready to be displayed")

    Rates_df = pd.DataFrame({"Rates": ["0-25",	"25-50",	"50-75",	"75-100",	"100-125",	"125-150",	"150-175",	"175-200",	"200-225",	"225-250",	"250-275",	"275-300",	"300-325",	"325-350",	"350-375",	"375-400",	"400-425",	"425-450",	"450-475",	"475-500",	"500-525",	"525-550",	"550-575",	"575-600",	"600-625",	"625-650",	"650-675",	"675-700",	"700-725",	"725-750",	"750-775",	"775-800",	"800-825",	"825-850",	"850-875",	"875-900",	"900-925",	"925-950",	"950-975",	"975-1000"]})

    #For each meeting date...
    for i in range (numberOfMeetingDates, 0, -1):

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

final_df = dfRatesMerger(dataframe_from_database1)

final_scrapped_df = final_df

dataframe_from_database1 = final_scrapped_df
# st.write((type(dataframe_from_database1)))
#Map function to replace European percentage type values in decimal type values : the percentage '65.0%' will be converted to '68.5 and '0,00' will be converted to '0'
def convert_percentage(x):
    if isinstance(x, str):
        value = (x.replace('%', ''))     
        # value = value.replace(',', '.')
        return value
    else:
        return x
        
#Function to convert the range value in column names to a single rate : 475-500' will be converted to '5'
def convertRateRanges(dataframe_from_database1):
    #Define the range values
    ranges = dataframe_from_database1.columns

    #Convert each range to its upper rate : the rate range '475-500' will be converted to '5'
    upperpoints = []
    for range_str in ranges:
        # Split the range string into its two values
        values = range_str.split("-")
        start_value = int(values[0])
        end_value = int(values[1])

        # Calculate the upperpoint
        upperpoint = end_value /100

        # Add the upperpoint to the list of upperpoints
        upperpoints.append(upperpoint)

    # print(upperpoints, "\n")

    dataframe_from_database1.columns = upperpoints

    dataframe_from_database1 = dataframe_from_database1.T
    # print(dataframe_from_database1)
    return dataframe_from_database1

def transformReworkedDataframeToDisplayableDataframe(dataframe_from_database1):
    #Replace European percentage type values in decimal type values 
    dataframe_from_database1 = dataframe_from_database1.map(convert_percentage)
    print(type(dataframe_from_database1))
    
    #Convert all percentages probabilities to float64
    for col in dataframe_from_database1.columns:
        if pd.api.types.is_numeric_dtype(dataframe_from_database1[col]):
            continue
        try:
            dataframe_from_database1[col] = pd.to_numeric(dataframe_from_database1[col])
        except:
            pass

    #Convert the range value in column names to a single rate :
    dataframe_from_database1 = convertRateRanges(dataframe_from_database1)

    # selected_columns = [dataframe_from_database1.columns[0], dataframe_from_database1.columns[1], dataframe_from_database1.columns[2], dataframe_from_database1.columns[3], dataframe_from_database1.columns[4], dataframe_from_database1.columns[5], dataframe_from_database1.columns[6], dataframe_from_database1.columns[7]]

    selected_columns = dataframe_from_database1.columns.tolist()

    # print("selected_columns", selected_columns, "\n")

    max_values_probability_rate = dataframe_from_database1[selected_columns].idxmax(axis=0)

    # print("max_values_indices", max_values_probability_rate, "\n")

    max_probability = dataframe_from_database1.max(axis=0)

    # print("max_values", max_probability, "\n")

    # # Print the indices of the maximum values in each row
    # print("max_values_indices", max_values_indices)

    df_to_display_in_graph1 = max_values_probability_rate.to_frame()
    df_to_display_in_graph1['Probabilities']=(max_probability)
    # Print the DataFrame
    df_to_display_in_graph1.columns = ['Upper range rate','Probabilities']
    return df_to_display_in_graph1

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

def dfRatesMerger(dataframe_from_database2):
    now = datetime.datetime.now()
    print("Starting data scrapping at : ", now.strftime("%H:%M:%S"))
    # st.write("Starting data scrapping")
    scrapped_data_from_website_df  = dataframe_from_database2
    numberOfMeetingDates = (len(scrapped_data_from_website_df)-1)
    now = datetime.datetime.now()
    print("Ending data scrapping at : ", now.strftime("%H:%M:%S"))
    # st.write("Data scrapping ended")
    # st.write("Data ready for cleaning")
    # st.write("Data ready to be displayed")

    Rates_df = pd.DataFrame({"Rates": ["0-25",	"25-50",	"50-75",	"75-100",	"100-125",	"125-150",	"150-175",	"175-200",	"200-225",	"225-250",	"250-275",	"275-300",	"300-325",	"325-350",	"350-375",	"375-400",	"400-425",	"425-450",	"450-475",	"475-500",	"500-525",	"525-550",	"550-575",	"575-600",	"600-625",	"625-650",	"650-675",	"675-700",	"700-725",	"725-750",	"750-775",	"775-800",	"800-825",	"825-850",	"850-875",	"875-900",	"900-925",	"925-950",	"950-975",	"975-1000"]})

    #For each meeting date...
    for i in range (numberOfMeetingDates, 0, -1):

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

final_df = dfRatesMerger(dataframe_from_database2)

final_scrapped_df = final_df

dataframe_from_database2 = final_scrapped_df
# st.write((type(dataframe_from_database2)))
#Map function to replace European percentage type values in decimal type values : the percentage '65.0%' will be converted to '68.5 and '0,00' will be converted to '0'
def convert_percentage(x):
    if isinstance(x, str):
        value = (x.replace('%', ''))     
        # value = value.replace(',', '.')
        return value
    else:
        return x
        
#Function to convert the range value in column names to a single rate : 475-500' will be converted to '5'
def convertRateRanges(dataframe_from_database2):
    #Define the range values
    ranges = dataframe_from_database2.columns

    #Convert each range to its upper rate : the rate range '475-500' will be converted to '5'
    upperpoints = []
    for range_str in ranges:
        # Split the range string into its two values
        values = range_str.split("-")
        start_value = int(values[0])
        end_value = int(values[1])

        # Calculate the upperpoint
        upperpoint = end_value /100

        # Add the upperpoint to the list of upperpoints
        upperpoints.append(upperpoint)

    # print(upperpoints, "\n")

    dataframe_from_database2.columns = upperpoints

    dataframe_from_database2 = dataframe_from_database2.T
    # print(dataframe_from_database2)
    return dataframe_from_database2

def transformReworkedDataframeToDisplayableDataframe(dataframe_from_database2):
    #Replace European percentage type values in decimal type values 
    dataframe_from_database2 = dataframe_from_database2.map(convert_percentage)
    print(type(dataframe_from_database2))
    
    #Convert all percentages probabilities to float64
    for col in dataframe_from_database2.columns:
        if pd.api.types.is_numeric_dtype(dataframe_from_database2[col]):
            continue
        try:
            dataframe_from_database2[col] = pd.to_numeric(dataframe_from_database2[col])
        except:
            pass

    #Convert the range value in column names to a single rate :
    dataframe_from_database2 = convertRateRanges(dataframe_from_database2)

    # selected_columns = [dataframe_from_database2.columns[0], dataframe_from_database2.columns[1], dataframe_from_database2.columns[2], dataframe_from_database2.columns[3], dataframe_from_database2.columns[4], dataframe_from_database2.columns[5], dataframe_from_database2.columns[6], dataframe_from_database2.columns[7]]

    selected_columns = dataframe_from_database2.columns.tolist()

    # print("selected_columns", selected_columns, "\n")

    max_values_probability_rate = dataframe_from_database2[selected_columns].idxmax(axis=0)

    # print("max_values_indices", max_values_probability_rate, "\n")

    max_probability = dataframe_from_database2.max(axis=0)

    # print("max_values", max_probability, "\n")

    # # Print the indices of the maximum values in each row
    # print("max_values_indices", max_values_indices)

    df_to_display_in_graph1 = max_values_probability_rate.to_frame()
    df_to_display_in_graph1['Probabilities']=(max_probability)
    # Print the DataFrame
    df_to_display_in_graph1.columns = ['Upper range rate','Probabilities']
    return df_to_display_in_graph1


df_to_display_in_graph1 = transformReworkedDataframeToDisplayableDataframe(dataframe_from_database1)

df_to_display_in_graph2 = transformReworkedDataframeToDisplayableDataframe(dataframe_from_database2)

# st.write(df_to_display_in_graph1)
# st.write(df_to_display_in_graph2)

# df_to_display_in_graph1

# ===== PYPLOT =====
# Create the line graph
plt.figure(figsize=(16, 6))
plt.plot(df_to_display_in_graph1.index, df_to_display_in_graph1['Upper range rate'], marker='o', linestyle='-')
plt.plot(df_to_display_in_graph2.index, df_to_display_in_graph2['Upper range rate'], marker='o', linestyle='-')
plt.xlabel('Meeting dates')
plt.ylabel('Upper range rate')
plt.title('Projected FED rates for upcoming meeting dates')
plt.grid(True)

# Scale Y axis by 0.25
def make_increment(start, end, num_steps):
    return [start + i * (end - start) / (num_steps - 1) for i in range(num_steps)]

max_value = df_to_display_in_graph1['Upper range rate'].max()
min_value = df_to_display_in_graph1['Upper range rate'].min()
increment_values = make_increment(max_value+0.25, min_value-0.25, int((max_value-min_value)/0.25)+3)
plt.gca().set_yticks(increment_values)

plt.show()

st.pyplot(plt)
