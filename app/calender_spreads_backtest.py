from helpers import downloadHistoricDataForSymbol, downloadHistoricDataForFuture
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd
from calender_spreads import calender_spread_spotter
from returns import returns_per_trade

def run_calender_spreads_backtest():
    col_names = ['symbol', 'date', 'expiry_date_curr', 'expiry_date_near', 'closing_price_curr', 'closing_price_near', 'difference', 'mean', 'std', 'upper_range', 'lower_range', 'signal']
    result_df = pd.DataFrame(columns = col_names)
    i = 0
    while(i<1200):
        temp_result_df = calender_spread_spotter(i)
        # print(temp_result_df)
        result_df = result_df.append(temp_result_df, ignore_index = True )
        print(i, end='\r')
        i = i + 1

    # print(result_df)
    result_df.to_csv('calender_spreads_signals.csv', index=False)
    return result_df

# def calculate_pl():
#     result_df = pd.read_csv('calender_spreads_signals.csv')
#     result_df = result_df.iloc[::-1].reset_index(drop=True)
#     i = 0
#     max_profit = 0
#     max_loss = 0
#     signal_count = 0
#     bad_signal_count = 0
#     while(i<result_df.shape[0]):
#         diff = result_df.iloc[i]['difference']
#         signal = result_df.iloc[i]['signal']
#         entry = result_df.iloc[i]['entry']
#         stoploss = result_df.iloc[i]['stoploss']
#         target = result_df.iloc[i]['target']
#  # and next_signal == 'Buy Spread'
#  # and next_signal == 'Sell Spread'
#         if(signal == 'Buy Spread'):
#             signal_count = signal_count + 1
#             temp_profit = target - diff
#             temp_loss = diff - stoploss
#             max_profit = max_profit + temp_profit
#             max_loss = max_loss + temp_loss
#                 # print("loss occured at " + str(i))
#
#         if(signal == 'Sell Spread'):
#             signal_count = signal_count + 1
#             temp_profit = diff - target
#             temp_loss = stoploss - diff
#             max_profit = max_profit + temp_profit
#             max_loss = max_loss + temp_loss
#
#                 # print("loss occured at " + str(i))
#         i = i + 1
#
#
#     # print(result_df.to_string())
#     print("max_profit = " + str(max_profit))
#     print("max_loss = " + str(max_loss))
#     print("signal count = " + str(signal_count))


def calculate_pl():
    returns_per_trade('calender_spreads_signals.csv', 'F&O_data/', 'calspread_wishlist.csv')
