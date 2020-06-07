import logging
import pickle
import csv
# import dateutil.parser as parser
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from nsepy import get_history
import json

exchange_list = ['NSE', 'BSE']
past_year_moving_data_flag = 0

def readFile(filename):
	with open(filename, 'rb') as fp:
		itemlist = pickle.load(fp)
	return itemlist

def readcsvFile(filename):
	itemlist = []
	with open(filename) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ',')
		for row in csv_reader:
			itemlist.append(row)
	itemlist = [item for sublist in itemlist for item in sublist]
	return itemlist

def writeJsonFile(filename, data_dict):
	with open(filename, 'w') as fp:
		json.dump(data_dict, fp)

def percentChange(a, b):
	return (b-a)*100/a

def mod(a):
	if (a<0):
		a = -a
	return a

def flatten(l):
	for item in l:
		try:
			yield from flatten(item)
		except TypeError:
			yield item

def downloadHistoricDataForSymbol(symbol, start_date, end_date, index_flag=False):
	data = get_history(symbol = symbol, start = start_date, end = end_date, index = index_flag)
	data.reset_index()
	return data

def pastDataForAnInstrument(symbol, exchange, timeframe = 'year'):
	# reads data for a time frame, convert to numpy array and reverses order
	instrument_ohlc = readFile("Past_year_moving_data" + "/" + str(symbol) + "_" + exchange)
	if (timeframe == 'month'):
		ohlc_sublist = instrument_ohlc[0:31]
	if(timeframe == 'year'):
		ohlc_sublist = instrument_ohlc

	open = []
	high = []
	low = []
	close = []
	date = []
	volume = []

	for element in ohlc_sublist:
		open.append(element['open'])
		high.append(element['high'])
		low.append(element['low'])
		close.append(element['close'])
		volume.append(element['volume'])
		date.append(element['date'])

	open = np.array(open, dtype = float)
	high = np.array(high, dtype = float)
	low = np.array(low, dtype = float)
	close = np.array(close, dtype = float)
	volume = np.array(volume, dtype = float)

	open = open[::-1]
	high = high[::-1]
	low = low[::-1]
	close = close[::-1]
	volume = volume[::-1]
	date = date[::-1]
	return {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume, 'date': date}

def globalDictForSingleStock(recognised_patterns, volumes, sup_res_dict, indicators):
	global_dict = {}
	date_list = []
	recognised_patterns_subdict = {}
	volumes_subdict = {}
	sup_res_dict_subdict = {}
	indicators_subdict = {}
	# converting datetime object to string here. Keep a note of this
	#list of last 10 working dats for an exchange
	for element in list(reversed(list(recognised_patterns)))[0:1]:
		date_list.append(element)
	# most recent first order followed here
	date_list = date_list[::-1]
	for element in date_list:
		recognised_patterns_subdict[str(element)] = recognised_patterns[element]
		volumes_subdict[str(element)] = volumes[element]
		sup_res_dict_subdict[str(element)] = sup_res_dict[element]

	for indicator_type, indicator_values in indicators.items():
		dummy_dict = {}
		for element in date_list:
			dummy_dict[str(element)] = indicator_values[element]

		indicators_subdict[indicator_type] = dummy_dict
	global_dict['Candlestick_patterns'] = recognised_patterns_subdict
	global_dict['Volumes'] = volumes_subdict
	global_dict['Support_and_Resistance'] = sup_res_dict_subdict
	global_dict['Indicators'] = indicators_subdict

	return global_dict