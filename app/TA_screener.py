import logging
import csv
import talib
from pathlib import Path
import numpy as np
from SandR_fractals import SandR_calc
# from SandR_fractals import plot_all
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from helpers import readFile, readcsvFile, writeJsonFile, percentChange, flatten, globalDictForSingleStock
# from Candlestick_patterns.marubozu import bullish_marubozu
from pattern_recognition import pattern_recogniser
from volume_filter import volume_screener
from sup_res_test import sup_res_calculator
from indicators import compute_indicators
import pandas as pd
from checklist import checklist
from trend_analysis import  find_trends

import json

end_date = date.today() + relativedelta(days=1)
# end_date = date.today() - relativedelta(days=102)

# print(end_date)
start_date = end_date - relativedelta(years=1)


def TA_screener(lookback_range):
    TA_results_global = {}
    count = 0
    col_name = ['symbol']
    wishlist_df = pd.read_csv('wishlist.csv', names=col_name)
    wishlist = wishlist_df.symbol.tolist()
    for element in wishlist:
        print(element)
        TA_results = {}
        df = pd.read_csv("stock_data/" + element + "_" + str(start_date) + "_" + str(end_date) + ".csv")
        print(df)
        open = df['Open']
        high = df['High']
        low = df['Low']
        close = df['Close']
        volume = df['Volume']
        date = df['Date']
        count = count + 1
        trends_dict = find_trends(df)
        recognised_patterns = pattern_recogniser(open, high, low, close, volume, date)
        volumes = volume_screener(volume, date)
        SandR_levels= SandR_calc(df)

        sup_res_dict = sup_res_calculator(close, date)
        indicators = compute_indicators(open, high, low, close, volume, date)

        TA_results = globalDictForSingleStock(recognised_patterns, volumes, sup_res_dict, SandR_levels, indicators, trends_dict, lookback_range)
        # print(TA_results)
        df = df.set_index("Date")
        trades = checklist(TA_results, df)
        TA_results_global[element] = trades

        if count == 5:
            return TA_results_global
        # break


    writeJsonFile("TA_screener_output.json", TA_results_global)
    return TA_results_global
# print(TA_results_global)


# TA_screener()
