import csv
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
from os import listdir
import os
import itertools
import json
from datetime import datetime, timedelta


class DataIntraday(btfeeds.GenericCSVData):
  params = (
      ('dtformat', ('%Y%m%d')),
      ('tmformat', ('%H:%M')),
      # fromdate=datetime(2019,6,3),
      # todate=datetime(2019,6,29),
      ('timeframe', bt.TimeFrame.Minutes),
      ('compression', 1),
      ('datetime', 1),
      ('time', 2),
      ('open', 3),
      ('high', 4),
      ('low', 5),
      ('close', 6),
      ('volume', 7),
      ('openinterest', 8)
  )


class MyStrategy(bt.Strategy):
    print('datas[0]')
    market_start = "9:20"
    market_end = "15:15"
    init_gap = 0
    banknifty_ohlc = pd.read_csv('nifty50_daily_data/combined_scrips_2019.csv')
    params = (('market_start', market_start),
              ('market_end', market_end),
              ('init_gap', init_gap),
              ('nifty50_ohlc_daily', banknifty_ohlc))

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or (str(self.datas[0].datetime.date(0)) + " " + str(self.datas[0].datetime.time(0)))
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        # print('%s, %s' % (dt.isoformat(), txt))
        print(dt + " " + str(txt))


    def notify_order(self, order):
        for index, data in enumerate(self.datas):
        # if order.status in [order.Submitted, order.Accepted]:
        #     # Buy/Sell order submitted/accepted to/by broker - Nothing to do
        #     self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
        #     self.order = order
        #     return
            # print(data._name)
            if order.status in [order.Expired]:
                self.log('BUY EXPIRED')

            elif order.status in [order.Completed]:
                if order.isbuy():
                    self.log(
                        'BUY EXECUTED, %s Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (data._name,
                         order.executed.price,
                         order.executed.value,
                         order.executed.comm))

                else:  # Sell
                    self.log('SELL EXECUTED, %s Price: %.2f, Cost: %.2f, Comm %.2f' %
                             (data._name,
                              order.executed.price,
                              order.executed.value,
                              order.executed.comm))

            # Sentinel to None: new orders allowed
            self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))


    def __init__(self):
        # self.intraday_data
        print("inside starategy class")

        # print(market_start)
    def next(self):
        # for datafeed in self.getdatanames():
        for index, data in enumerate(self.datas):
            datetime_obj = bt.num2date(data.datetime[0])
            time_obj = datetime_obj.time()
            curr_time = str(time_obj.hour)+ ":" +str(time_obj.minute)
            curr_date = str(datetime_obj.date())
            prev_date = str(datetime_obj.date() - timedelta(1))
            # entry = 0 set entry price on the basis of current outstanding order
            # print(prev_date)
            # banknifty_ohlc = pd.read_csv('BANKNIFTY_2019_ohlc.csv')
             # and  (self.p.nifty50_ohlc_daily['Symbol'] == data._name)
            # print(self.p.nifty50_ohlc_daily)
            symbol = data._name[:-5]
            # print(symbol)
            daily_data = self.p.nifty50_ohlc_daily.loc[self.p.nifty50_ohlc_daily['Symbol'] == symbol]
            daily_data = daily_data.reset_index(drop=True)
            # print((daily_data))
            # print((daily_data[(daily_data['Date'] == curr_date)].index.values[0]))
            data_row = daily_data[(daily_data['Date'] == curr_date)].index.values[0].item() - 1
            # print(type(data_row))
            # print(daily_data.iloc[data_row, 0])
            prev_high = daily_data.iloc[data_row, 2]
            prev_low = daily_data.iloc[data_row, 3]
            prev_close = daily_data.iloc[data_row, 4]
            # prev_close = 100
            gap = (data.open[0] - prev_close)/prev_close

            if(curr_time == self.p.market_start):
                self.p.init_gap = abs(gap)
                if(gap<=-0.01):
                    print(str(gap) + "    " + str(4))
                    print("current open = " + str(data.open[0]))
                    print("previous day close = " + str(prev_close))

                    # entry = 100
                    # self.log('BUY CREATE, %.2f' % self.data.close[0])
                    self.buy()

                if(gap>=0.01):
                    print(str(gap) + "    " + str(5))
                    # entry = 100
                    # self.log('sell CREATE, %.2f' % self.data.close[0])
                    self.sell()

            if self.position:
                # print(self.p.init_gap)
                if(curr_time == self.p.market_end):
                    # print((self.getposition(self.datas[0].Size)))
                    print(str(gap) + "    " + str(1))
                    self.close()

                if (-0.2 * self.p.init_gap <= gap <= 0.2 * self.p.init_gap):
                    print(str(gap) + "    " + str(2))
                    self.close()

                if ((gap >= 1.5 * self.p.init_gap) or (gap <= -1.5 * self.p.init_gap)):
                    print(str(gap) + "    " + str(3))
                    self.close()



if __name__ == '__main__':

    # data_intraday = DataIntraday(dataname='banknifty_minute_data/BANKNIFTY_2019.csv')
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)

    data_files = os.listdir('/home/parallax/algo_trading/app/day_trading_strategies/test_minute_data')
    print(data_files)
    count_break = 0
    for element in data_files:
        filename = '/home/parallax/algo_trading/app/day_trading_strategies/test_minute_data/' + element
        data_intraday = DataIntraday(dataname=filename)
        cerebro.adddata(data_intraday)
        print("feed loaded")
        count_break = count_break + 1
        if (count_break == 1):
            break




    # data_daily =



    cerebro.broker.setcash(100000)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
