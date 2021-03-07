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


def checklist(ta_dict, df):
    print(df)
    symbol = df['Symbol'].unique()[0]
    print(symbol)
    trades = {}
    sideways_patterns = {'spinning top', 'doji'}
    bullish_patterns = ['bullish marubozu', 'hammer', 'bullish engulfing', 'piercing', 'bullish harami', 'morning star']
    bearish_patterns = ['bearish marubozu', 'hanging man', 'shooting star', 'bearish engulfing', 'dark cloud cover',
                        'bearish harami', 'evening star']

    score = 0
    indicators_available = ['BBANDS', 'MACD', 'RSI']
    mean_candle_length = (df['High'] - df['Low']).mean()
    tolerance = 0.5 * mean_candle_length
    curr_close = df[-1:]['Close'].values[0]
    curr_date = df.index[-1]
    print(curr_date)
    print(tolerance)
    print(curr_close)
    candlestick_patterns_list = ta_dict['Candlestick_patterns']
    volumes = ta_dict['Volumes']
    sup_res_dict = ta_dict['Support_and_Resistance'][curr_date]
    indicators = ta_dict['Indicators'][curr_date]
    sandr_fractals, levels = ta_dict['SandR_fractals'][curr_date]
    # print(sup_res_dict)
    valid_patterns_flag = 0
    s_and_r_flag = 0
    above_avg_volumes_flag = 0
    date = next(iter(candlestick_patterns_list))

    # Volumes
    patterns_list = [list(dict.keys())[0] for dict in candlestick_patterns_list[date]]
    for pattern in patterns_list:
        if pattern in bullish_patterns:
            score += 1
        elif pattern in bearish_patterns:
            score -= 1
        else:
            score = 0

    # Support and Resistance (fractals)
    fractals_array = np.asarray(sandr_fractals, dtype=np.float32)
    try:
        closest_support = fractals_array[fractals_array < curr_close].max()
    except ValueError:
        closest_support = None
    try:
        closest_resistance = fractals_array[fractals_array > curr_close].min() or None
    except:
        closest_resistance = None
    print(f'closest_support = {closest_support}')
    print(f'closest_resistance = {closest_resistance}')
    if closest_support and (curr_close - closest_support) <= tolerance:
        score_add = 1
        score = score + score_add
    elif closest_resistance and (closest_resistance - curr_close) <= tolerance:
        score_add = -1
        score = score + score_add
    else:
        pass

    # Support and Resistance (trendln)
    support = sup_res_dict['Support']
    resistance = sup_res_dict['Resistance']
    if (curr_close - support) <= tolerance:
        score_add = 1
        score = score + score_add
    elif (resistance - curr_close) <= tolerance:
        score_add = -1
        score = score + score_add
    else:
        pass

    # Indicators
    print(indicators)
    for indicator, indicator_val in indicators.items():
        if indicator == 'BBANDS':
            if (curr_close - indicator_val['lowerband']) <= tolerance:
                score_add = 1
                score = score + score_add
            if (indicator_val['upperband'] - curr_close) <= tolerance:
                score_add = -1
                score = score + score_add
        if indicator == 'RSI':
            if (indicator_val <= 20):
                score_add = 1
                score = score + score_add
            if indicator_val >= 80:
                score_add = -1
                score = score + score_add
        if indicator == 'MACD':
            if indicator_val > 0:
                score_add = 1
                score = score + score_add
            if indicator_val < 0:
                score_add = -1
                score = score + score_add

    print(score)
    curr_volumes = next(iter(volumes[date]))
    above_avg_volumes_pct = volumes[date][curr_volumes]
    if above_avg_volumes_pct > 0:
        if score > 0:
            score_add = 1
            score = score + score_add
        if score < 0:
            score_add = -1
            score = score + score_add
        # print(score_add)


    ta_dict['Candlestick_patterns'] = candlestick_patterns_list[date]
    ta_dict['Volumes'] = next(iter(volumes[date]))
    ta_dict['Volume_pct'] = above_avg_volumes_pct
    ta_dict['Support_and_Resistance'] = sup_res_dict
    temp_dict = {}
    # for element in indicators_available:
    #     print(indicators)
    #     indicator = indicators[element]
    #     temp_dict[element] = indicator[date]
    ta_dict['Indicators'] = indicators
    ta_dict['Score'] = score
    # trades[symbol] = ta_dict
    return ta_dict
