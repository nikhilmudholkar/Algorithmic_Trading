from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd

def returns_per_trade(signal_filename, data_source, wishlist):
    result_df = pd.read_csv(signal_filename)
    result_df = result_df.iloc[::-1].reset_index(drop=True)

    relevent_symbols = result_df['symbol'].unique()
    print(relevent_symbols)
    signal_ignore_count = 0
    col_names = ['symbol', 'entry_date', 'exit_date', 'expiry_date_curr', 'expiry_date_near', 'closing_price_curr', 'closing_price_near', 'difference', 'mean', 'std', 'upper_range', 'lower_range', 'signal', 'entry', 'exit', 'target', 'stoploss', 'pnl', 'returns']
    trades_df = pd.DataFrame(columns = col_names)
    for element in relevent_symbols:
        symbol = element
        # print(symbol)
        signals = result_df.loc[result_df['symbol'] == symbol]
        # print(signals)
        data_curr_month = pd.read_csv(data_source + symbol + '_curr_month.csv', index_col=None)
        data_near_month = pd.read_csv(data_source + symbol + '_near_month.csv', index_col=None)
        parsed_dates = []
        for index, row in signals.iterrows():
            # print("===========================================")
            date = row['date']
            expiry_date_curr = row['expiry_date_curr']
            expiry_date_near = row['expiry_date_near']
            diff = row['difference']
            signal = row['signal']
            entry = row['entry']
            target = row['target']
            stoploss = row['stoploss']

            if(date in parsed_dates):
                signal_ignore_count = signal_ignore_count + 1
                continue
            date = datetime.strptime(date, '%Y-%m-%d')
            pnl = 0
            exit = 0
            trade_closed_flag = False
            iter = 0
            new_date = date
            while(trade_closed_flag!= True):
                new_date = date + relativedelta(days = iter)
                new_date = new_date.strftime('%Y-%m-%d')
                new_date = str(new_date)
                if((new_date in data_curr_month['Date'].tolist()) and (new_date in data_near_month['Date'].tolist())):
                    parsed_dates.append(new_date)
                    temp_curr_month = data_curr_month.loc[data_curr_month['Date'] == new_date]
                    temp_near_month = data_near_month.loc[data_near_month['Date'] == new_date]
                    temp_curr_month = temp_curr_month.reset_index()
                    temp_near_month = temp_near_month.reset_index()
                    temp_diff = temp_near_month['Close'] - temp_curr_month['Close']
                    temp_diff = temp_diff.iloc[0]
                    # print("temp_diff = " + str(temp_diff))
                    # print("target = " + str(target))
                    # print("stoploss = " + str(stoploss))
                    if(signal == 'Buy Spread'):
                        if(temp_diff >= target):
                            trade_closed_flag = True
                            pnl = (target - entry) + (temp_diff - target)
                            exit = temp_diff
                        if(temp_diff <= stoploss):
                            trade_closed_flag = True
                            pnl = (stoploss - entry) + (temp_diff - stoploss)
                            exit = temp_diff
                    if(signal == 'Sell Spread'):
                        if(temp_diff <= target):
                            trade_closed_flag = True
                            pnl = (entry - target) + (target - temp_diff)
                            exit = temp_diff
                        if(temp_diff >= stoploss):
                            trade_closed_flag = True
                            pnl = (entry - stoploss) + (stoploss - temp_diff)
                            exit = temp_diff

                    # to cancel the trade when expiry is reached for current month or trade active for more than 5 days
                    if(trade_closed_flag==False):
                        if(new_date == expiry_date_curr or iter>=5):
                            if(signal == 'Buy Spread'):
                                pnl = temp_diff - entry
                                exit = temp_diff
                            if(signal == 'Sell Spread'):
                                pnl = entry - temp_diff
                                exit = temp_diff
                            print(pnl)
                            break
                iter = iter + 1
                # new_date = datetime.strptime(new_date, '%Y-%m-%d')
            exit_date = new_date
            if(entry!=0):
                returns  = round(pnl/abs(entry), 4)
            else:
                returns = 0
            temp_list = [symbol, date, exit_date, expiry_date_curr, expiry_date_near, row['closing_price_curr'], row['closing_price_near'], diff, row['mean'], row['std'], row['upper_range'], row['lower_range'], signal, entry, exit, target, stoploss, pnl, returns]
            trades_df.loc[len(trades_df)] = temp_list
    print("signals_ignored = " + str(signal_ignore_count))
                # break
    trades_df.to_csv('calender_spread_trades.csv', index = False)

            # break
