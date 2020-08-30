from helpers import downloadHistoricDataForSymbol, downloadHistoricDataForFuture
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd
from nsepy.derivatives import get_expiry_date

def data_downloader_stock():
    end_date = date.today() + relativedelta(days = 1)
    start_date = end_date - relativedelta(years = 1)
    print(end_date)
    with open('/home/parallax/algo_trading/app/wishlist.csv', 'r') as wishlist:
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]
            data = downloadHistoricDataForSymbol(symbol, start_date, end_date)
            file_name = "/home/parallax/algo_trading/app/stock_data/" + symbol + "_" + str(start_date) + "_" + str(end_date) + ".csv"
            data.to_csv(file_name, index = True)
            print("data downloaded for " + symbol)
            # break

    with open('/home/parallax/algo_trading/app/index_wishlist.csv', 'r') as wishlist:
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            index_flag = True
            symbol = element[0]
            symbol.replace('_', " ")
            if(symbol == 'NIFTY 50'):
                symbol = 'NIFTY'
            if(symbol == 'NIFTY Bank'):
                symbol = 'BANKNIFTY'
            data = downloadHistoricDataForSymbol(symbol, start_date, end_date, index_flag)
            file_name = "/home/parallax/algo_trading/app/stock_data/" + symbol + "_" + str(start_date) + "_" + str(end_date) + ".csv"
            data.to_csv(file_name, index = True)
            print("data downloaded for " + symbol)
            # break
    return 'success'

def data_downloader_FnO_daily():
    with open('/home/parallax/algo_trading/app/wishlist.csv', 'r') as wishlist:
        symbol_count = 0
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]
            symbol.replace('_', " ")
            print(symbol)
            today = date.today()
            symbol_count = symbol_count + 1
            first_day = today
            i = 0
            curr_frames =[]
            near_frames = []
            existing_current_month_data = pd.read_csv('/home/parallax/algo_trading/app/F&O_data/' + symbol + '_curr_month.csv')
            existing_near_month_data = pd.read_csv('/home/parallax/algo_trading/app/F&O_data/' + symbol + '_near_month.csv')

            while(i<2):
                curr_day = today - relativedelta(days = i)
                curr_day_str = curr_day.strftime('%Y-%m-%d')
                if((curr_day_str not in existing_near_month_data['Date'].tolist()) or (curr_day_str not in existing_current_month_data['Date'].tolist())):
                    expiry_date_curr_month = list(get_expiry_date(curr_day.year, curr_day.month))
                    data_curr_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_curr_month))
                    data_curr_month.reset_index(level=0, inplace=True)
                    curr_frames.append(data_curr_month)
                    near_day = curr_day + relativedelta(months = 1)
                    expiry_date_near_month = list(get_expiry_date(near_day.year, near_day.month))
                    data_near_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_near_month))
                    data_near_month.reset_index(level=0, inplace=True)
                    near_frames.append(data_near_month)
                    # break
                i = i + 1

            curr_frames.append(existing_current_month_data)
            near_frames.append(existing_near_month_data)
            curr_month_data = pd.concat(curr_frames)
            curr_filename = "/home/parallax/algo_trading/app/F&O_data/" + symbol + "_curr_month.csv"
            curr_month_data.to_csv(curr_filename, index = False)
            near_month_data = pd.concat(near_frames)
            near_filename = "/home/parallax/algo_trading/app/F&O_data/" + symbol + "_near_month.csv"
            near_month_data.to_csv(near_filename, index = False)
            print("data downloaded for " + symbol)
            # break;
    return "success"


def data_downloader_FnO_historical(range):
    with open('wishlist.csv', 'r') as wishlist:
        symbol_count = 0
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]
            symbol.replace('_', " ")
            print(symbol)
            today = date.today()
            symbol_count = symbol_count + 1
            index_flag = False
            if(symbol_count<40):
                continue
            # only until 39 does wishlist contains stocks
            if(symbol_count>=40):
                index_flag = True
            first_day = today
            i = 0
            curr_frames =[]
            near_frames = []
            while(i<range):
                curr_day = today - relativedelta(days = i)
                curr_day_str = curr_day.strftime('%Y-%m-%d')
                expiry_date_curr_month = list(get_expiry_date(curr_day.year, curr_day.month))
                data_curr_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_curr_month), index_flag = index_flag)
                data_curr_month.reset_index(level=0, inplace=True)
                curr_frames.append(data_curr_month)
                near_day = curr_day + relativedelta(months = 1)
                expiry_date_near_month = list(get_expiry_date(near_day.year, near_day.month))
                data_near_month = downloadHistoricDataForFuture(symbol, start_date = curr_day, end_date = curr_day, expiry_date = max(expiry_date_near_month), index_flag = index_flag)
                data_near_month.reset_index(level=0, inplace=True)
                near_frames.append(data_near_month)
                    # break
                i = i + 1
            curr_month_data = pd.concat(curr_frames)
            curr_filename = "F&O_data/" + symbol + "_curr_month.csv"
            curr_month_data.to_csv(curr_filename, index = False)
            near_month_data = pd.concat(near_frames)
            near_filename = "F&O_data/" + symbol + "_near_month.csv"
            near_month_data.to_csv(near_filename, index = False)
            # break;
    return "success"
