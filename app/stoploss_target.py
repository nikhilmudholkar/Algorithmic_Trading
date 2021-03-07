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

bullish_patterns = ['bullish marubozu', 'hammer', 'bullish engulfing', 'piercing', 'bullish harami', 'morning star']
bearish_patterns = ['bearish marubozu', 'hanging man', 'shooting star', 'bearish engulfing', 'dark cloud cover', 'bearish harami', 'evening star']

def stoploss(trades):
    stoploss_dict = {}
    for symbol, ta_dict in trades.items():
        stoploss_list = []
        candlestick_patterns = ta_dict['Candlestick_patterns']

        for pattern in candlestick_patterns:
            stoploss = 0
            low = 0
            for patten_name, pattern_values in pattern.items():
                date = next(iter(pattern_values))
                stoploss = min(pattern_values[date])
                for day, ohlc in pattern_values.items():
                    low = ohlc[2]
                    stoploss = min(low, stoploss)
                    print(stoploss)

                # print(stoploss)
                stoploss_list.append(stoploss)
        stoploss_dict[symbol] = stoploss_list
    # print(stoploss_dict)
    return stoploss_dict

def target(trades):
    target_dict = {}
    for symbol, ta_dict in trades.items():
        s_and_r = ta_dict['Support_and_Resistance']
        support = s_and_r['Support']
        resistance = s_and_r['Resistance']
        candlestick_patterns = ta_dict['Candlestick_patterns']
        for pattern in candlestick_patterns:
            for pattern_name, pattern_values in pattern.items():
                print(pattern_name)
                if(pattern_name in bullish_patterns):
                    target_dict[symbol] = resistance
                else:
                    target_dict[symbol] = support
    # print(target_dict)
    return target_dict
