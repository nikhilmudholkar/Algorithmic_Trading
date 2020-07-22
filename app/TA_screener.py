import logging
import csv
import talib
from pathlib import Path
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from helpers import readFile, readcsvFile, writeJsonFile, percentChange, flatten, globalDictForSingleStock
# from Candlestick_patterns.marubozu import bullish_marubozu
from pattern_recognition import pattern_recogniser
from volume_filter import volume_screener
from sup_res_test import sup_res_calculator
from indicators import compute_indicators
import pandas as pd
import json

end_date = date.today()
# print(end_date)
start_date = end_date - relativedelta(years = 1)
def TA_screener():
	TA_results_global = {}
	count = 0
	col_name = ['symbol']
	wishlist_df = pd.read_csv('wishlist.csv', names = col_name)
	wishlist = wishlist_df.symbol.tolist()
	for element in wishlist:
		TA_results = {}
		df = pd.read_csv("stock_data/" + element + "_" + str(start_date) + "_" + str(end_date) + ".csv")
		open = df['Open']
		high = df['High']
		low = df['Low']
		close = df['Close']
		volume = df['Volume']
		date = df['Date']
		recognised_patterns = pattern_recogniser(open, high, low, close, volume, date)
		volumes = volume_screener(volume, date)
		sup_res_dict = sup_res_calculator(close, date)
		indicators = compute_indicators(open, high, low, close, volume, date)
		TA_results = globalDictForSingleStock(recognised_patterns, volumes, sup_res_dict, indicators)
		TA_results_global[element] = TA_results

	writeJsonFile("TA_screener_output.json", TA_results_global)
	# print(TA_results_global)


# TA_screener()
