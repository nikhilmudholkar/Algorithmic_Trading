from helpers import downloadHistoricDataForSymbol
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import pandas as pd

def data_downloader():
    end_date = date.today()
    start_date = end_date - relativedelta(years = 1)
    print(end_date)
    with open('wishlist.csv', 'r') as wishlist:
        csv_reader = csv.reader(wishlist)
        for element in csv_reader:
            symbol = element[0]

            data = downloadHistoricDataForSymbol(symbol, start_date, end_date)
            # print(data)
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


    return "success"







# data = downloadHistoricDataForSymbol(symbol, start_date, end_date)
# print(data)
