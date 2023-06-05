import pandas as pd
import requests
import time
from datetime import datetime
import openpyxl


#* changes date to UNIX
def datetime_to_timestamp(datetime_str):
    try:
        date_format = f"%d-%m-%Y %H:%M"
        datetime_obj = datetime.strptime(datetime_str, date_format)
        timestamp = datetime_obj.timestamp()
        return int(timestamp)
    except ValueError:
        print("Invalid datetime format. Please use the format 'day-month-year hour:minute' (e.g., 25-05-2023 14:30).")
        
        
#* collects information
input_datetime_start = input("Enter the start date (day-month-year hour:minute): ")
unix_timestamp_start = datetime_to_timestamp(input_datetime_start)
input_datetime_end = input("Enter the end date (day-month-year hour:minute): ")
unix_timestamp_end = datetime_to_timestamp(input_datetime_end)

unix_start = []
unix_stop = []

#* loop that divides the timestamps into days
while int(unix_timestamp_start) <= int(unix_timestamp_end):
    unix_start.append(int(unix_timestamp_start))
    unix_timestamp_start = int(unix_timestamp_start) + 86400
    unix_stop.append(int(unix_timestamp_start))


#* choose crypto and intervals
symbol = input(str('Choose the coins pair (e.g., BTC-USDT): '))
interval = input(str('Choose the candles intervals (e.g., 1min): '))




#* sends a data request
def request(symbol, start_time_unix, end_time_unix, interval):

    url = f"https://api.kucoin.com/api/v1/market/candles?type={interval}&symbol={symbol}&startAt={start_time_unix}&endAt={end_time_unix}"
    response = requests.get(url)
    data = response.json()

    if data['code'] != '200000':
        print(f"Error: {data['msg']}")
        #! saves the file from corupting from 'Too many requests' error
        time.sleep(4)
        request(symbol, start_time_unix, end_time_unix, interval)
        print('saved')
    else:
        return data['data']
    
#* creates an empty excel file 
workbook = openpyxl.Workbook()
workbook.save(f'{symbol}_{interval}_candles.xlsx')


df_old = pd.read_excel(f'{symbol}_{interval}_candles.xlsx')


#* requests and connects the data 
for x in range(len(unix_start)):
    data = request(symbol, unix_start[x], unix_stop[x], interval) 
    time.sleep(4)
    df_new = pd.DataFrame(data)
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_old = df_combined
    
#* appends the data to the file
df_combined.to_excel(f'{symbol}_{interval}_candles.xlsx', index=False)
print('done')
