import numpy
import talib

def compute_indicators(open, high, low, close, volume, date):

	indicators = {}
	indicator_types = ['RSI', 'MACD', 'BBANDS']
	indicator_count = len(indicator_types)
	indicator_values = []
	rsi = talib.RSI(close, timeperiod = 14)
	indicator_values.append(rsi)

	macd, macdsignal, macdhist= talib.MACD(close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
	indicator_values.append(macdhist)

	upperband, middleband, lowerband = talib.BBANDS(close, timeperiod = 20, nbdevup = 2, nbdevdn = 2, matype = 0)
	BB_list = []
	band_length = len(upperband)
	i = 0

	while (i<band_length):
		local_dict = {}
		local_dict['upperband'] = upperband[i]
		local_dict['middleband'] = middleband[i]
		local_dict['lowerband'] = lowerband[i]
		BB_list.append(local_dict)
		i = i+1
	indicator_values.append(BB_list)
	# print(indicator_values)
	# while (len(indicators) != indicator_count):
	# 	i = 0
	# 	local_indicator = {}
	# 	local_indicator_val = indicator_values.pop()
	# 	while (i<len(date)):
	# 		print()
	#
	# 		local_indicator[indicator_types.pop()] = local_indicator_val[i]
	# 		i = i+1
	# 	indicators[date[i]] = local_indicator
	# return indicators

	i = 0
	while i < len(date):
		local_indicator = {}
		while len(local_indicator) < indicator_count:
			local_indicator[indicator_types[len(local_indicator)-1]] = indicator_values[len(local_indicator)-1][i]

		indicators[date[i]] = local_indicator
		i=i+1
	# print(indicators)
	return indicators
