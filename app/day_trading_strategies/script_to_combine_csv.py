import os
import glob
import pandas as pd
os.chdir("/home/parallax/algo_trading/app/day_trading_strategies/2019_minute_data")



# extension = 'csv'
# all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
# print(all_filenames)
all_foldernames = ['NIFTY50_JAN2019', 'NIFTY50_FEB2019', 'NIFTY50_MAR2019',
                   'NIFTY50_APR2019', 'NIFTY50_MAY2019', 'NIFTY50_JUN2019',
                   'NIFTY50_JUL2019', 'NIFTY50_AUG2019', 'NIFTY50_SEP2019',
                   'NIFTY50_OCT2019', 'NIFTY50_NOV2019', 'NIFTY50_DEC2019' ]

# update this list when new proper data arrives
nifty50_list= ['JSWSTEEL','TATASTEEL','BPCL','HINDALCO','HDFCBANK','ADANIPORTS','GRASIM',
               'ULTRACEMCO','GAIL','ONGC','POWERGRID','KOTAKBANK','INFY','AXISBANK','NTPC',
               'COALINDIA','CIPLA','INDUSINDBK','SBIN','TECHM','HEROMOTOCO','ICICIBANK',
               'EICHERMOT','DRREDDY','BAJAJ-AUTO','TITAN','BHARTIARTL','TATAMOTORS','LT','TCS','HDFC',
               'ITC','BAJFINANCE','MARUTI','HINDUNILVR','IOC','WIPRO',
               'SUNPHARMA','ASIANPAINT','RELIANCE','M&M','HCLTECH','UPL','NIFTY','BANKNIFTY']

def combine_across_months():
    os.chdir("/home/parallax/algo_trading/app/day_trading_strategies/2019_minute_data")
    for symbol in nifty50_list:
        combined_csv = pd.DataFrame()
        all_filenames = []
        for month in all_foldernames:
            filename = month + "/" + symbol + ".txt"
            all_filenames.append(filename)

        print(all_filenames)
        combined_csv = pd.concat([pd.read_csv(f, sep=",", header=None) for f in all_filenames ])
        # print(combined_csv)
        combined_csv.columns = ['Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open_Interest']
        target_filename = "nifty50_minute_data/" + symbol + "_2019.csv"
        combined_csv.to_csv(target_filename, index=False, encoding='utf-8-sig')


def combine_across_scrips():
    os.chdir("/home/parallax/algo_trading/app/day_trading_strategies")
    all_filenames = []
    for symbol in nifty50_list:
        combined_csv = pd.DataFrame()
        filename = "nifty50_daily_data/" + symbol + "_2015-10-13_2020-10-13.csv"
        # JSWSTEEL_2015-10-13_2020-10-13
        all_filenames.append(filename)
        # print(pd.read_csv(filename, header=None))
    combined_csv = pd.concat([pd.read_csv(f, header=None, skiprows=1) for f in all_filenames])
    combined_csv.columns = ['Date','Symbol','Series','Prev Close','Open','High','Low','Last','Close','VWAP','Volume','Turnover','Trades','Deliverable Volume','%Deliverble']
    target_filename = "nifty50_daily_data/combined_scrips_2019.csv"
    combined_csv.to_csv(target_filename, index=False, encoding='utf-8-sig')
    # print(all_filenames)

combine_across_scrips()
