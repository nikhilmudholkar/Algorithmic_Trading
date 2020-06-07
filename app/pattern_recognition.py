import numpy
import talib



def pattern_recogniser(open, high, low, close, volume, date):
	recognised_patterns = {}
	marubozu = talib.CDLMARUBOZU(open, high, low, close)
	spinning_top = talib.CDLSPINNINGTOP(open, high, low, close)
	doji = talib.CDLDOJI(open, high, low, close)
	hammer = talib.CDLHAMMER(open, high, low, close)
	hanging_man = talib.CDLHANGINGMAN(open, high, low, close)
	shooting_star = talib.CDLSHOOTINGSTAR(open, high, low, close)
	engulfing = talib.CDLENGULFING(open, high, low, close)
	piercing = talib.CDLPIERCING(open, high, low, close)
	dark_cloud_cover = talib.CDLDARKCLOUDCOVER(open, high, low, close)
	harami = talib.CDLHARAMI(open, high, low, close)
	morning_star = talib.CDLMORNINGSTAR(open, high, low, close, penetration=0.75)
	evening_star = talib.CDLEVENINGSTAR(open, high, low, close, penetration=0.75)
	i = 0
	while (i<len(date)):
		patterns = []
		sentiments = [100, -100]
		if(marubozu[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			if (marubozu[i] == 100):
				pattern_name = "bullish marubozu"
			else:
				pattern_name = "bearish marubozu"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(spinning_top[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "spinning top"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(doji[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "doji"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(hammer[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "hammer"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(hanging_man[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "hanging man"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(shooting_star[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "shooting star"
			curr_date = date[i]
			ohlc_list = [open[i], high[i], low[i], close[i]]
			temp_dict[curr_date] = ohlc_list
			rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		# engulfing[i] = 100
		if(engulfing[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			if (i>0):
				if (engulfing[i] == 100):
					pattern_name = "bullish engulfing"
				else:
					pattern_name = "bearish engulfing"
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if (piercing[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "piercing"
			if (i>0):
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if (dark_cloud_cover[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "dark cloud cover"
			if (i>0):
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		if(harami[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			if (i>0):
				if (engulfing[i] == 100):
					pattern_name = "bullish harami"
				else:
					pattern_name = "bearish harami"
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		# morning_star[i] = 100
		if(morning_star[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "morning star"
			if (i>1):
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				prev_prev_date = date[i-2]
				prev_prev_ohlc_list = [open[i-2], high[i-2], low[i-2], close[i-2]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				temp_dict[prev_prev_date] = prev_prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		# evening_star[i] = 100
		if(evening_star[i] in sentiments):
			rec_pattern = {}
			temp_dict = {}
			pattern_name = "evening star"
			if (i>1):
				curr_date = date[i]
				curr_ohlc_list = [open[i], high[i], low[i], close[i]]
				prev_date = date[i-1]
				prev_ohlc_list = [open[i-1], high[i-1], low[i-1], close[i-1]]
				prev_prev_date = date[i-2]
				prev_prev_ohlc_list = [open[i-2], high[i-2], low[i-2], close[i-2]]
				temp_dict[curr_date] = curr_ohlc_list
				temp_dict[prev_date] = prev_ohlc_list
				temp_dict[prev_prev_date] = prev_prev_ohlc_list
				rec_pattern[pattern_name] = temp_dict
			patterns.append(rec_pattern)

		recognised_patterns[date[i]] = patterns

		i = i+1

	return recognised_patterns
