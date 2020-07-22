from helpers import downloadHistoricDataForSymbol, downloadHistoricDataForFuture
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd

def calender_spread_spotter(range):
    signal_count = 0
    with open('wishlist.csv', 'r') as wishlist:

        csv_reader = csv.reader(wishlist)
        col_names = ['symbol', 'date', 'expiry_date_curr', 'expiry_date_near', 'closing_price_curr', 'closing_price_near', 'difference', 'mean', 'std', 'upper_range', 'lower_range', 'signal', 'entry', 'target', 'stoploss']
        result_df = pd.DataFrame(columns = col_names)
        for element in csv_reader:
            signal = "no signal"
            symbol = element[0]
            symbol.replace('_', " ")
            curr_filename = "F&O_data/" + symbol + "_curr_month.csv"
            near_filename = "F&O_data/" + symbol + "_near_month.csv"
            curr_df = pd.read_csv(curr_filename)
            near_df = pd.read_csv(near_filename)
            new_curr_df = curr_df.filter(['Date', 'Close', 'Expiry'])
            new_near_df = near_df.filter(['Date', 'Close', 'Expiry'])
            spreads_df = pd.merge(new_curr_df, new_near_df, on='Date')
            spreads_df.rename(columns = {'Close_x':'curr_month_close',
                                         'Close_y':'near_month_close',
                                         'Expiry_x':'curr_month_expiry',
                                         'Expiry_y':'near_month_expiry'}, inplace = True)

            spreads_df = spreads_df.loc[range:]
            spreads_df['difference'] = (spreads_df['near_month_close'] - spreads_df['curr_month_close'])
            spreads_df['difference'] = spreads_df['difference'].round(decimals = 2)
            # diff_mean = round(spreads_df['difference'].loc[:60].mean(), 2)
            # diff_std = round(spreads_df['difference'].loc[:60].std(), 2)

            diff_mean = round(spreads_df['difference'].mean(), 2)
            diff_std = round(spreads_df['difference'].std(), 2)

            diff_mean = pd.to_numeric(diff_mean)
            diff_std = pd.to_numeric(diff_std)
            upper_range = round(diff_mean + 2.5*diff_std, 2)
            lower_range = round(diff_mean - 2.5*diff_std, 2)
            current_spread = spreads_df['difference'].iloc[0]
            if(current_spread >= upper_range):
                signal_count = signal_count + 1
                signal = "Sell Spread"
                entry = current_spread
                target = entry - 1.5*diff_std
                stoploss = entry + 0.5*diff_std

            if(current_spread <= lower_range):
                signal_count = signal_count + 1
                signal = 'Buy Spread'
                entry = current_spread
                # target = diff_mean - diff_std
                # stoploss = diff_mean - 3*diff_std
                target = entry + 1.5*diff_std
                stoploss = entry - 0.5*diff_std
                # print(str(symbol) + " SELL CURRENT MONTH, BUY NEAR MONTH")

            # print("signal_count = " + str(signal_count))
            # print("**********************************************************")

            date = spreads_df['Date'].iloc[0]
            expiry_date_curr = spreads_df['curr_month_expiry'].iloc[0]
            expiry_date_near = spreads_df['near_month_expiry'].iloc[0]
            closing_price_curr = spreads_df['curr_month_close'].iloc[0]
            closing_price_near = spreads_df['near_month_close'].iloc[0]


            # result_df.loc[len(result_df)] = temp_list
            if((signal!="no signal") and date != expiry_date_curr):
                temp_list = [symbol, date, expiry_date_curr, expiry_date_near, closing_price_curr, closing_price_near, current_spread, diff_mean, diff_std, upper_range, lower_range, signal, entry, target, stoploss]
                result_df.loc[len(result_df)] = temp_list
            # break;

            # print("exception occured for: " + str(symbol))
    # print(result_df)
    return result_df
