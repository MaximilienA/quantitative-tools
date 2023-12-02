#IMPORTS
import pandas as pd
import datetime as dt
import datetime
from datetime import timedelta 
import yfinance as yf 
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# import sys
# sys.path.append('../')

import backend.database

# import plotly.express as px

# number_of_days = 150

#DATA FRAME FOR MATCHING INDEX NAME WITH INDEX SYMBOL
data  = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    'Index_symbol': ['^FCHI', '^DJI', '^IXIC', '^NYA', '^XAX', '^RUT', '^VIX', '^FTSE', '^GDAXI', '^GSPC', '^STOXX50E', '^N100', '^BFX', 'IMOEX.ME', '^N225', '^HSI', '000001.SS', '399001.SZ', '^STI', '^AXJO', '^AORD', '^BSESN', '^JKSE', '^KLSE', '^NZ50', '^KS11', '^TWII', '^GSPTSE', '^BVSP', '^MXX', '^IPSA', '^MERV', '^TA125.TA', '^CASE30', '^JN0U.JO', '^NSEI'],
    'Index_name': ['CAC 40', 'Dow Jones Industrial Average', 'NASDAQ Composite', 'NYSE COMPOSITE (DJ)', 'NYSE AMEX COMPOSITE INDEX', 'Russell 2000', 'CBOE Volatility Index', 'FTSE 100', 'DAX PERFORMANCE-INDEX', 'S&P 500', 'ESTX 50 PR.EUR', 'Euronext 100 Index', 'BEL 20', 'MOEX Russia Index', 'Nikkei 225', 'HANG SENG INDEX', 'SSE Composite Index', 'Shenzhen Index', 'STI Index', 'S&P/ASX 200', 'ALL ORDINARIES', 'S&P BSE SENSEX', 'IDX COMPOSITE', 'FTSE Bursa Malaysia KLCI', 'S&P/NZX 50 INDEX GROSS ( GROSS', 'KOSPI Composite Index', 'TSEC weighted index', 'S&P/TSX Composite index', 'IBOVESPA', 'IPC MEXICO', 'S&P/CLX IPSA', 'MERVAL', 'TA-125', 'EGX 30 Price Return Index', 'Top 40 USD Net TRI Index', 'NIFTY 50']
}
df_index_name = pd.DataFrame(data)

#FUNCTION TO GET THE NUMBERS OF DAYS BETWEEN THE FIRST DATE OF THE INDEX DATA AND TODAY
def get_first_day_of_stock_price(tickerA, tickerB):
    data = yf.download(tickerA, period="max")
    first_day_of_tickerA = data.index[0]

    data = yf.download(tickerB, period="max")
    first_day_of_tickerB = data.index[0]

    print("first_day_of_tickerA : ", first_day_of_tickerA, "first_day_of_tickerB", first_day_of_tickerB, "\n")
    print("Number of days returned", min((datetime.date.today() - first_day_of_tickerA.date()).days, (datetime.date.today() - first_day_of_tickerB.date()).days))
    return min((datetime.date.today() - first_day_of_tickerA.date()).days, (datetime.date.today() - first_day_of_tickerB.date()).days)

#FUNCTION THAT RETURNS THE TABLE OF DATES AND CORRELATIONS
def correlation_computer(number_days, indexNameA, indexNameB):
    #SETTING DATES
    start_input = (pd.to_datetime('today').normalize()- timedelta(days = number_days)- timedelta(days = 29))
    end_input = (pd.to_datetime('today').normalize()+ timedelta(days = 0))
    # print(start_input)
    # print(end_input)
    #GET PRICES for assetA
    #YFINANCE : GET assetA PRICES
    stock_labA = df_index_name[df_index_name.Index_name == indexNameA].Index_symbol.values[0]
    stockA = yf.Ticker(stock_labA)
    stock_history = stockA.history(start=start_input, end=end_input )
    df_history_assetA = stock_history['Close'][-(29+number_days):]
    df_history_assetA.index = df_history_assetA.index.tz_localize(None)
    # print("\ndf_history_assetA.shape : ",df_history_assetA.shape)
    # print("df_history_assetA : ",df_history_assetA)

    #GET PRICES for assetB
    #YFINANCE : GET assetB PRICES
    stock_labB = df_index_name[df_index_name.Index_name == indexNameB].Index_symbol.values[0]
    stockB = yf.Ticker(stock_labB)
    stock_history = stockB.history(start=start_input, end=end_input)
    df_history_assetB = stock_history['Close'][-(29+number_days):]
    df_history_assetB.index = df_history_assetB.index.tz_localize(None)
    # print("\ndf_history_assetB.shape : ",df_history_assetB.shape)
    # print("df_history_assetB : ",df_history_assetB)

    start_input = start_input.strftime("%Y-%m-%d")
    end_input = end_input.strftime("%Y-%m-%d")

    # print("\nstart_input : ", start_input, " end_input : ", end_input)

    np_start_date = np.datetime64(start_input)
    np_end_date = np.datetime64(end_input)

    # print("\nnp_start_date : ", np_start_date, " np_end_date : ", np_end_date)

    #MERGE assetA AND assetB PRICES DATASETS
    merge=pd.merge(df_history_assetA,df_history_assetB, how='outer', on='Date') #outer to keep all dates
    merge = merge.rename(columns={'Close_x' : 'Close_assetA', 'Close_y' : 'Close_assetB'})
    # print("\nMerge.shape : ", merge.shape)
    merge = merge.sort_index(ascending=True) #reorder dates 
    # print("\nmerge1", merge)

    #REPLACE EMPTY FIRST CELLS FOR assetA CLOSE PRICES (WEEK ENDS, DAYS OFF)

    #ASSET TRADED EVERY DAY
    if (stock_labB == "BTC-USD"):
        # try : 
        if merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetA'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D'), 'Close_assetA'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D'), 'Close_assetA']:
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
        elif merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetA'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D'), 'Close_assetA'] :
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')]
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')]
        elif merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetA'] :
            merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetA"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')]
        # print("merge2", merge)

        #REPLACE EMPTY CELLS FOR assetA CLOSE PRICES
        for i in merge.index:
            if merge.isnull().at[i, 'Close_assetA']:
                merge["Close_assetA"][i] = merge["Close_assetA"][(i - timedelta(days=1)).strftime("%Y-%m-%d")]
        # print("merge3", merge)

        #REPLACE EMPTY FIRST CELLS FOR assetB CLOSE PRICES (WEEK ENDS, DAYS OFF)
        if merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB']:
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-3,'D')]
        elif merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB'] and merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB'] :
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')]
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-2,'D')]
        elif merge.isnull().at[np.datetime64(np_end_date)- np.timedelta64(len(merge),'D'), 'Close_assetB'] :
            merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge),'D')] = merge["Close_assetB"][np.datetime64(np_end_date)- np.timedelta64(len(merge)-1,'D')]
        # print("merge4", merge)

        #REPLACE EMPTY CELLS FOR assetB CLOSE PRICES
        for i in merge.index:
            if merge.isnull().at[i, 'Close_assetB']:
                merge["Close_assetB"][i] = merge["Close_assetB"][(i - timedelta(days=1)).strftime("%Y-%m-%d")]
        # except Exception : 
        #     print(merge["Close_assetA"][i])

    #ASSET TRADED DURING WEEKDAYS
    else:
        merge['Close_assetA'] = merge['Close_assetA'].fillna(0)
        
        if merge['Close_assetA'].iloc[0] == 0 and merge['Close_assetA'].iloc[1] == 0  and merge['Close_assetA'].iloc[2] == 0 :
            merge['Close_assetA'].iloc[0] = merge['Close_assetA'].iloc[3]
            merge['Close_assetA'].iloc[1] = merge['Close_assetA'].iloc[3]
            merge['Close_assetA'].iloc[2] = merge['Close_assetA'].iloc[3]
        elif merge['Close_assetA'].iloc[0] == 0 and merge['Close_assetA'].iloc[1] == 0:
            merge['Close_assetA'].iloc[0] = merge['Close_assetA'].iloc[2]
            merge['Close_assetA'].iloc[1] = merge['Close_assetA'].iloc[2]
        elif merge['Close_assetA'].iloc[0] == 0:
            merge['Close_assetA'].iloc[0] = merge['Close_assetA'].iloc[1]

        for i in range(len(merge)):
            if merge['Close_assetA'].iloc[i] == 0 :
                merge['Close_assetA'].iloc[i] = merge['Close_assetA'].iloc[i+1]

        merge['Close_assetB'] = merge['Close_assetB'].fillna(0)

        if merge['Close_assetB'].iloc[0] == 0 and merge['Close_assetB'].iloc[1] == 0  and merge['Close_assetB'].iloc[2] == 0 :
            merge['Close_assetB'].iloc[0] = merge['Close_assetB'].iloc[3]
            merge['Close_assetB'].iloc[1] = merge['Close_assetB'].iloc[3]
            merge['Close_assetB'].iloc[2] = merge['Close_assetB'].iloc[3]
        elif merge['Close_assetB'].iloc[0] == 0 and merge['Close_assetB'].iloc[1] == 0:
            merge['Close_assetB'].iloc[0] = merge['Close_assetB'].iloc[2]
            merge['Close_assetB'].iloc[1] = merge['Close_assetB'].iloc[2]
        elif merge['Close_assetB'].iloc[0] == 0:
            merge['Close_assetB'].iloc[0] = merge['Close_assetB'].iloc[1]
        
        for i in range(len(merge)):
            if merge['Close_assetB'].iloc[i] == 0 :
                merge['Close_assetB'].iloc[i] = merge['Close_assetB'].iloc[i+1]

    # print("merge5", merge)

    #COMPUTE DAILY RETURNS FOR assetA AND assetB
    merge["daily_return_assetA"] = (merge["Close_assetA"].pct_change(1))*100
    merge["daily_return_assetB"] = (merge["Close_assetB"].pct_change(1))*100

    # print("merge6", merge)

    #REPLACE EMPTY CELLS FOR assetA AND assetB RETURNS

    #ASSET TRADED EVERY DAY
    if (stock_labB == "BTC-USD"):
        for i in merge.index:
            if merge.isnull().at[i, 'daily_return_assetA']:
                merge["daily_return_assetA"][i] = merge["daily_return_assetA"][(i + timedelta(days=1)).strftime("%Y-%m-%d")]
            if merge.isnull().at[i, 'daily_return_assetB']:
                merge["daily_return_assetB"][i] = merge["daily_return_assetB"][(i + timedelta(days=1)).strftime("%Y-%m-%d")]

        # print("Index names of table_to_display : ", merge.index.dtype)
        # print(type(merge.index))
        # print(type(merge))
        # print(merge.index,"\n")

    #ASSET TRADED DURING WEEKDAYS
    else:
        merge['daily_return_assetA'] = merge['daily_return_assetA'].fillna(0)

        for i in range(len(merge)):
            if merge['daily_return_assetA'].iloc[i] == 0 :
                merge['daily_return_assetA'].iloc[i] = merge['daily_return_assetA'].iloc[i+1]

        merge['daily_return_assetB'] = merge['daily_return_assetB'].fillna(0)
        
        for i in range(len(merge)-1):
            if merge['daily_return_assetB'].iloc[i] == 0 :
                merge['daily_return_assetB'].iloc[i] = merge['daily_return_assetB'].iloc[i+1]
    print("len(merge)", len(merge))         
    print("merge7", merge)
    #INITIALIZE ONE SERIE FOR DATES AND ONE FOR CORRELATION COEFFICIENT r_price
    liste_r_price = pd.Series(dtype = 'float64')
    liste_end_date = pd.Series(dtype = 'datetime64[ns]')
    # print("Liste end date =", liste_end_date,"\n")
    for i in range(len(merge['Close_assetA'])-29):
        # print(i) 
        range_assetA = merge['Close_assetA'][0+i:30+i]
        range_assetB = merge['Close_assetB'][0+i:30+i]
        # print(range_assetA)
        # print(range_assetB)
        # print(range_assetA.shape,range_assetB.shape)
        r_price = np.corrcoef(range_assetA, range_assetB)
        r_price = r_price[0,1]
        liste_r_price = pd.concat([liste_r_price, pd.Series([r_price])])
        liste_end_date = pd.concat([liste_end_date, pd.Series(merge['Close_assetB'][29+i:30+i].index.values)])
        # print(liste_end_date)
        # liste_end_date = liste_end_date.append(pd.Series(merge['Close_assetB'][29+i:30+i].index.values))

    # print("\nType de la date dans la liste", liste_end_date.dtype) 
    # print("\nliste_r_price", liste_r_price) 
    # print("\nliste_end_date", liste_end_date) 
    # print(type(liste_r_price))
    # print(type(liste_end_date))
    # print((range_assetA))
    # print((range_assetB))
    # print("merge['Close_assetB'][30:31].index.values ",merge['Close_assetB'][29:30].index.values)
    # print(merge.index.dtype)

    # liste_end_date = pd.to_datetime(liste_end_date.index).tz_localize(None)
    # print(type(liste_r_price))
    # print(type(liste_end_date))
    # print(liste_r_price)
    # print(liste_end_date)

    # print("len(liste_r_price) : ", len(liste_r_price))
    # print("len(liste_end_date) : ", len(liste_end_date))

    table_to_display = pd.DataFrame({'Correlations' : liste_r_price, 'Date' : liste_end_date})
    # print("Table to display : \n", (table_to_display))
    # print("Type de la date dans la table", table_to_display.Date.dtype)
    # print("Index names of table_to_display : ", table_to_display.index.dtype)
    # print(type(table_to_display.index))
    # print(type(table_to_display))
    # print(table_to_display.index)

    print("Finale table : ", table_to_display)
    return table_to_display

#DISPLAY GRAP ON WEBPAGE WITH STREAMLIT
#run in a classic VSC terminal : "streamlit run c:\Users\pluto\Desktop\Investissement\Python\Correlation\Version-steamlit.py".
st.header("Correlation graph")
index_name_list = df_index_name["Index_name"].tolist()
selected_name = st.selectbox("Select first index", index_name_list, index = 2)
selected_nameB = st.selectbox("Select second index", index_name_list, index = 9)
print("selected_name", selected_name, " ", selected_nameB)
#CALL THE FUNCTION TO RETRIEVE DATE AND COMPUTE CORRELATIONS
# number_of_days = get_first_day_of_stock_price(df_index_name[df_index_name.Index_name == selected_name].Index_symbol.values[0], df_index_name[df_index_name.Index_name == selected_nameB].Index_symbol.values[0])
number_of_days = 1000
table = correlation_computer(number_of_days, selected_name, selected_nameB)

#WITH PLOTLY WITH SLIDER
fig = go.Figure()
fig.add_trace(go.Scatter(x=table['Date'], y=table['Correlations'], mode='lines', name=selected_name + " - " + selected_nameB +  " 30 days correlation" + " (last " + str(number_of_days)+ " days )"))
fig.update_layout(
    title=selected_name + " - " + selected_nameB +  " 30 days correlation" + " (last " + str(number_of_days)+ " days )",
    xaxis=dict(title='Date'),
    yaxis=dict(title='Correlation'),
)
fig.update_layout(xaxis_rangeslider_visible=True)

# DISPLAY GRAPH IN WINDOWS POP UP WINDOW
# st.pyplot(plt)
st.plotly_chart(fig)

now = datetime.datetime.now()
formatted_time = now.strftime("%H:%M:%S")


backend.database.insertdata(selected_name)
backend.database.insertdata(str(datetime.date.today()))
backend.database.insertdata(str(formatted_time))