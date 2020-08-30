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


def checklist(TA_results_dict):
    trades = {}
    for symbol, ta_dict in TA_results_dict.items():
        indicators_available = ['BBANDS', 'MACD', 'RSI']
        candlestick_patterns = ta_dict['Candlestick_patterns']
        volumes = ta_dict['Volumes']
        sup_res_dict = ta_dict['Support_and_Resistance']
        indicators = ta_dict['Indicators']
        valid_patterns_flag = 0
        s_and_r_flag = 0
        above_avg_volumes_flag = 0
        # print(candlestick_patterns)
        date = next(iter(candlestick_patterns))
        # print(date)

        if(len(candlestick_patterns[date])!=0):
            valid_patterns_flag = 1

        curr_volumes = next(iter(volumes[date]))
        above_avg_volumes_flag = volumes[date][curr_volumes]

        if(valid_patterns_flag == 1 and above_avg_volumes_flag == 1):
            ta_dict['Candlestick_patterns'] =candlestick_patterns[date]
            ta_dict['Volumes'] = next(iter(volumes[date]))
            ta_dict['Support_and_Resistance'] = sup_res_dict[date]
            temp_dict = {}
            for element in indicators_available:
                indicator = indicators[element]
                temp_dict[element] = indicator[date]
            ta_dict['Indicators'] = temp_dict
            trades[symbol] = ta_dict
    return trades
