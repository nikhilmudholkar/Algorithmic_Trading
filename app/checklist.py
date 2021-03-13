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
import logging

logger = logging.getLogger(name=__name__)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='app.log',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def checklist(ta_dict, df, lookback):
    # print(ta_dict)
    # print(df)
    symbol = df['Symbol'].unique()[0]
    # print(symbol)
    trades = {}
    sideways_patterns = {'spinning top', 'doji'}
    bullish_patterns = ['bullish marubozu', 'hammer', 'bullish engulfing', 'piercing', 'bullish harami', 'morning star']
    bearish_patterns = ['bearish marubozu', 'hanging man', 'shooting star', 'bearish engulfing', 'dark cloud cover',
                        'bearish harami', 'evening star']

    score = 0
    flags = []
    indicators_available = ['BBANDS', 'MACD', 'RSI']
    mean_candle_length = (df['High'] - df['Low']).mean()
    tolerance = 0.1 * mean_candle_length
    curr_close = df[-lookback:]['Close'].values[0]
    curr_date = df.index[-lookback]
    # print(curr_date)
    # candlestick_patterns_list = ta_dict['Candlestick_patterns']
    # print(candlestick_patterns_list)
    volumes = ta_dict['Volumes'][curr_date]
    # print(volumes)
    sup_res_dict = ta_dict['Support_and_Resistance'][curr_date]
    indicators = ta_dict['Indicators'][curr_date]
    sandr_fractals, levels = ta_dict['SandR_fractals'][curr_date]
    candlestick_patterns_list = ta_dict['Candlestick_patterns'][curr_date]
    # print(sup_res_dict)
    valid_patterns_flag = 0
    s_and_r_flag = 0
    above_avg_volumes_flag = 0
    # date = next(iter(candlestick_patterns_list))

    # CandleStick patterns
    patterns_list = [list(dict.keys())[0] for dict in candlestick_patterns_list]
    for pattern in patterns_list:
        # print(pattern)
        if pattern in bullish_patterns:
            # print()
            score += 1
            flags.append(f"CandleStick Patterns bullish: {pattern}")
            logger.info(f'bullish pattern found: {pattern} in {symbol}')
        if pattern in bearish_patterns:
            score -= 1
            flags.append(f"CandleStick Patterns bearish: {pattern}")
            logger.info(f'bearish pattern found: {pattern} in {symbol}')

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
    # print(f'closest_support = {closest_support}')
    # print(f'closest_resistance = {closest_resistance}')
    if closest_support and (curr_close - closest_support) <= tolerance:
        score_add = 1
        score = score + score_add
        flags.append('Fractals S&R bullish')
    if closest_resistance and (closest_resistance - curr_close) <= tolerance:
        score_add = -1
        score = score + score_add
        flags.append('Fractals S&R bearish')

    # Support and Resistance (trendln)
    support = sup_res_dict['Support']
    resistance = sup_res_dict['Resistance']
    if (curr_close - support) <= tolerance:
        score_add = 1
        score = score + score_add
        flags.append('Trend S&R bullish')
    if (resistance - curr_close) <= tolerance:
        score_add = -1
        score = score + score_add
        flags.append('Trend S&R bearish')

    # Indicators
    # print(indicators)
    for indicator, indicator_val in indicators.items():
        if indicator == 'BBANDS':
            if (curr_close - indicator_val['lowerband']) <= tolerance:
                score_add = 1
                score = score + score_add
                flags.append(f'Indcators: {indicator} bullish')
            if (indicator_val['upperband'] - curr_close) <= tolerance:
                score_add = -1
                score = score + score_add
                flags.append(f'Indicators: {indicator} bearish')
        if indicator == 'RSI':
            print(indicator_val)
            if indicator_val <= 20:
                score_add = 1
                score = score + score_add
                flags.append(f'Indicators: {indicator} bullish')
            if indicator_val >= 80:
                score_add = -1
                score = score + score_add
                flags.append(f'Indicators: {indicator} bearish')
        # if indicator == 'MACD':
        #     if indicator_val > 0:
        #         score_add = 1
        #         score = score + score_add
        #         flags.append(f'Indicators: {indicator} bullish')
        #     if indicator_val < 0:
        #         score_add = -1
        #         score = score + score_add
        #         flags.append(f'Indicators: {indicator} bearish')

    # print(score)
    curr_volumes = list(volumes.keys())[0]
    # print(curr_volumes)
    above_avg_volumes_pct = volumes[curr_volumes]
    if above_avg_volumes_pct > 0:
        if score > 0:
            score_add = 1
            score = score + score_add
            flags.append('Volumes bullish')
        if score < 0:
            score_add = -1
            score = score + score_add
            flags.append('Volumes bearish')
        # print(score_add)

    ta_dict['Candlestick_patterns'] = candlestick_patterns_list
    ta_dict['Volumes'] = next(iter(volumes))
    ta_dict['Volume_pct'] = above_avg_volumes_pct
    ta_dict['Support_and_Resistance'] = sup_res_dict
    temp_dict = {}
    # for element in indicators_available:
    #     print(indicators)
    #     indicator = indicators[element]
    #     temp_dict[element] = indicator[date]
    ta_dict['Indicators'] = indicators
    ta_dict['Score'] = score
    ta_dict['Symbol'] = symbol
    ta_dict['Flags'] = flags
    return ta_dict
