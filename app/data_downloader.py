from helpers import downloadHistoricDataForSymbol, downloadHistoricDataForFuture
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd
from nsepy.derivatives import get_expiry_date

def data_downloader_stock():
    end_date = date.today()
    start_date = end_date - relativedelta(years = 1)
    print(end_date)
    with open('wishlist.csv', 'r') as wishlist:
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]
            data = downloadHistoricDataForSymbol(symbol, start_date, end_date)
            file_name = "stock_data/" + symbol + "_" + str(start_date) + "_" + str(end_date) + ".csv"
            data.to_csv(file_name, index = True)
            print("data downloaded for " + symbol)

    with open('index_wishlist.csv', 'r') as wishlist:
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            index_flag = True
            symbol = element[0]
            symbol.replace('_', " ")
            data = downloadHistoricDataForSymbol(symbol, start_date, end_date, index_flag)
            file_name = "stock_data/" + symbol + "_" + str(start_date) + "_" + str(end_date) + ".csv"
            data.to_csv(file_name, index = True)
            print("data downloaded for " + symbol)
    return 'success'

def data_downloader_FnO_historical():
    with open('wishlist.csv', 'r') as wishlist:
        symbol_count = 0
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]
            symbol.replace('_', " ")
            print(symbol)
            today = date.today()
            symbol_count = symbol_count + 1
            first_day = today
            i = 1
            curr_frames = []
            near_frames = []
            while(i<1000):
                curr_day = today - relativedelta(days = i)
                expiry_date_curr_month = list(get_expiry_date(curr_day.year, curr_day.month))
                data_curr_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_curr_month))
                curr_frames.append(data_curr_month)
                near_day = curr_day + relativedelta(months = 1)
                expiry_date_near_month = list(get_expiry_date(near_day.year, near_day.month))
                data_near_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_near_month))
                near_frames.append(data_near_month)
                # break
                i = i + 1
            curr_month_data = pd.concat(curr_frames)
            curr_filename = "F&O_data/" + symbol + "_curr_month.csv"
            curr_month_data.to_csv(curr_filename, index = True)
            near_month_data = pd.concat(near_frames)
            near_filename = "F&O_data/" + symbol + "_near_month.csv"
            near_month_data.to_csv(near_filename, index = True)
            # break;
    return "success"
