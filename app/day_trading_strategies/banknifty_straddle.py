import csv
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
import backtrader.strategies as btstrats
from os import listdir
import os
import itertools
import json
from datetime import datetime, timedelta
import pyfolio as pf


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
    target_hit_count = 0
    stoploss_hit_count = 0
    market_end_hit_count = 0
    params = (('market_start', market_start),
              ('market_end', market_end),
              ('init_gap', init_gap),
              ('nifty50_ohlc_daily', banknifty_ohlc),
              ('target_hit_count', target_hit_count),
              ('stoploss_hit_count', stoploss_hit_count),
              ('market_end_hit_count', market_end_hit_count))

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or (str(self.datas[0].datetime.date(0)) + " " + str(self.datas[0].datetime.time(0)))
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print(dt + " " + str(txt))


    def notify_order(self, order):
        for index, data in enumerate(self.datas):
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
            self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))


    def __init__(self):
        print("inside starategy class")
    def next(self):
        for index, data in enumerate(self.datas):
            datetime_obj = bt.num2date(data.datetime[0])
            time_obj = datetime_obj.time()
            curr_time = str(time_obj.hour)+ ":" +str(time_obj.minute)
            curr_date = str(datetime_obj.date())
            prev_date = str(datetime_obj.date() - timedelta(1))
            symbol = data._name[:-5]
            daily_data = self.p.nifty50_ohlc_daily.loc[self.p.nifty50_ohlc_daily['Symbol'] == symbol]
            daily_data = daily_data.reset_index(drop=True)
            prev_data_row = daily_data[(daily_data['Date'] == curr_date)].index.values[0].item() - 1
            prev_high = daily_data.iloc[prev_data_row, 2]
            prev_low = daily_data.iloc[prev_data_row, 3]
            prev_close = daily_data.iloc[prev_data_row, 4]
            gap = (data.open[0] - prev_close)/prev_close

            if(curr_time == self.p.market_start):
                self.p.init_gap = abs(gap)
                if(gap<=-0.02):
                    print(str(gap) + "    " + str(4))
                    print("current open = " + str(data.open[0]))
                    print("previous day close = " + str(prev_close))
                    self.buy(size = 25)

                if(gap>=0.01):
                    print(str(gap) + "    " + str(5))
                    self.sell(size = 25)

            if self.position:
                if(curr_time == self.p.market_end):
                    print(str(gap) + "    " + str(1))
                    self.p.target_hit_count += 1
                    self.close()

                if (-0.2 * self.p.init_gap <= gap <= 0.2 * self.p.init_gap):
                    print(str(gap) + "    " + str(2))
                    self.p.stoploss_hit_count += 1
                    self.close()

                if ((gap >= 1.5 * self.p.init_gap) or (gap <= -1.5 * self.p.init_gap)):
                    print(str(gap) + "    " + str(3))
                    self.p.market_end_hit_count += 1
                    self.close()
    def stop(self):
        print('number of times target hit = ' + str(self.p.target_hit_count))
        print('number of times stoploss hit = ' + str(self.p.stoploss_hit_count))
        print('number of times market end reached = ' + str(self.p.market_end_hit_count))


if __name__ == '__main__':
    data_files = os.listdir('/home/parallax/algo_trading/app/day_trading_strategies/test_minute_data')
    print(data_files)
    for element in data_files:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(MyStrategy)
        cerebro.addanalyzer(btanalyzers.SharpeRatio, timeframe=bt.TimeFrame.Minutes, compression=1, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        print(element)
        # if(element == 'BANKNIFTY_2019.csv'):
        #     continue
        filename = '/home/parallax/algo_trading/app/day_trading_strategies/test_minute_data/' + element
        data_intraday = DataIntraday(dataname=filename)
        cerebro.adddata(data_intraday)
        print("feed loaded")
        cerebro.broker.setcash(800000)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        thestrats = cerebro.run()
        thestrat = thestrats[0]
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        print('Sharpe Ration = ' , thestrat.analyzers.sharpe.get_analysis())
        pyfoliozer = thestrat.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
        print(returns)
        print(positions)
        print(transactions)
        print(gross_lev)
        pf.create_full_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        gross_lev=gross_lev,
        live_start_date='2020-01-01',  # This date is sample specific
        round_trips=True)
