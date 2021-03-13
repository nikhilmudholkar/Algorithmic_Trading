import logging
import pickle
import csv
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from nsepy import get_history
import json
import multiprocessing as mp
from multiprocessing import Process, Pipe
import multiprocessing.pool
import timeout_decorator
import os
from functools import wraps
import errno
import signal

exchange_list = ['NSE', 'BSE']
past_year_moving_data_flag = 0


class NoDaemonProcess(multiprocessing.Process):
	# make 'daemon' attribute always return False
	def _get_daemon(self):
		return False

	def _set_daemon(self, value):
		pass

	daemon = property(_get_daemon, _set_daemon)


class Pool(multiprocessing.pool.Pool):
	Process = NoDaemonProcess


def readFile(filename):
	with open(filename, 'rb') as fp:
		itemlist = pickle.load(fp)
	return itemlist


def readcsvFile(filename):
	itemlist = []
	with open(filename) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			itemlist.append(row)
	itemlist = [item for sublist in itemlist for item in sublist]
	return itemlist


def writeJsonFile(filename, data_dict):
	with open(filename, 'w') as fp:
		json.dump(data_dict, fp)


def percentChange(a, b):
	return (b - a) * 100 / a


def mod(a):
	if (a < 0):
		a = -a
	return a


def flatten(l):
	for item in l:
		try:
			yield from flatten(item)
		except TypeError:
			yield item


# @timeout_decorator.timeout(10, use_signals = False)
def downloadHistoricDataForSymbol(symbol, start_date, end_date, index_flag=False):
	data = get_history(symbol=symbol, start=start_date, end=end_date, index=index_flag)
	data.reset_index()
	return data


# @timeout_decorator.timeout(10, use_signals = False)
def downloadHistoricDataForFuture(symbol, start_date, end_date, expiry_date, index_flag=False):
	data = get_history(symbol=symbol, start=start_date, end=end_date, index=index_flag)
	data.reset_index()
	return data


def pastDataForAnInstrument(symbol, exchange, timeframe='year'):
	# reads data for a time frame, convert to numpy array and reverses order
	instrument_ohlc = readFile("Past_year_moving_data" + "/" + str(symbol) + "_" + exchange)
	if timeframe == 'month':
		ohlc_sublist = instrument_ohlc[0:31]
	if timeframe == 'year':
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

	open = np.array(open, dtype=float)
	high = np.array(high, dtype=float)
	low = np.array(low, dtype=float)
	close = np.array(close, dtype=float)
	volume = np.array(volume, dtype=float)

	open = open[::-1]
	high = high[::-1]
	low = low[::-1]
	close = close[::-1]
	volume = volume[::-1]
	date = date[::-1]
	return {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume, 'date': date}


def globalDictForSingleStock(recognised_patterns, volumes, sup_res_dict, SandR_levels, indicators, trends_dict,
							 lookback_range):
	global_dict = {}
	date_list = []
	recognised_patterns_subdict = {}
	volumes_subdict = {}
	sup_res_dict_subdict = {}
	indicators_subdict = {}
	SandR_levels_dict = {}
	trends_subdict = {}
	# converting datetime object to string here. Keep a note of this
	# list of last 10 working dats for an exchange
	for element in list(reversed(list(recognised_patterns)))[0:lookback_range]:
		date_list.append(element)
	# most recent first order followed here
	date_list = date_list[::-1]

	for element in date_list:
		recognised_patterns_subdict[str(element)] = recognised_patterns[element]
		volumes_subdict[str(element)] = volumes[element]
		sup_res_dict_subdict[str(element)] = sup_res_dict[element]
		SandR_levels_dict[str(element)] = SandR_levels
		# print(trends_dict)
		trends_subdict[str(element)] = trends_dict[element]
		# print(trends_subdict[str(element)])

	# for indicator_type, indicator_values in indicators.items():
	# 	dummy_dict = {}
	# 	for element in date_list:
	# 		dummy_dict[str(element)] = indicator_values[element]

	# indicators_subdict[indicator_type] = dummy_dict
	for element in date_list:
		indicators_subdict[str(element)] = indicators[element]

	global_dict['Candlestick_patterns'] = recognised_patterns_subdict
	global_dict['Volumes'] = volumes_subdict
	global_dict['Support_and_Resistance'] = sup_res_dict_subdict
	global_dict['SandR_fractals'] = SandR_levels_dict
	global_dict['Indicators'] = indicators_subdict
	global_dict['Trends'] = trends_subdict

	return global_dict


def sort_trades_dict(trades_dict):
	scores_dict_bullish = {}
	scores_dict_bearish = {}
	scores_dict_sideways = {}
	for symbol, TA_dict in trades_dict.items():
		score = TA_dict['Score']
		if score>0:
			scores_dict_bullish[symbol] = score
		elif score<0:
			scores_dict_bearish[symbol] = score
		else:
			scores_dict_sideways[symbol] = score


	sorted_dict_bullish = {k: v for k, v in sorted(scores_dict_bullish.items(), key=lambda item: item[1], reverse=True)}
	sorted_dict_bearish = {k: v for k, v in sorted(scores_dict_bearish.items(), key=lambda item: item[1])}
	sorted_dict_sideways = scores_dict_sideways
	# print(sorted_dict)
	trades_dict['Sorted_dict_bullish'] = sorted_dict_bullish
	trades_dict['Sorted_dict_bearish'] = sorted_dict_bearish
	trades_dict['Sorted_dict_sideways'] = sorted_dict_sideways
	return trades_dict
