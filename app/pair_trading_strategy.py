import math
import datetime
import numpy as np
import pandas as pd
import pprint
import matplotlib.pyplot as plt
import matplotlib
# matplotlib.use('Agg')
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import scipy.stats
import os
from types import SimpleNamespace
from evaluate_pairs import evaluate_pairs
import pyqstrat as pq

pq.set_defaults()

def zscore_indicator(symbol, timestamps, indicators, strategy_context):
    residuals = indicators.residuals
    r = pd.Series(residuals).rolling(window = 130) #tune this parameter
    mean = r.mean()
    std = r.std(ddof = 0)
    zscore = (residuals - mean) / std
    zscore = np.nan_to_num(zscore)
    print(symbol)
    print(zscore)
    return zscore

# CHECK THIS FUNCTION LOGIC
def pair_strategy_signal(contract_group, timestamps, indicators, parent_signals, strategy_context):
    zscore = indicators.zscore
    # print((timestamps))
    # print(strategy_context.s1_symbol)
    # print(strategy_context.s2_symbol)
    # symbol_list.remove(symbol_1)
    # print(contract_group)
    signal = np.where(zscore > 2, 2, 0)
    signal = np.where(zscore < -2, -2, signal)

    # target
    signal = np.where((zscore < 1) & (zscore > 0.5), 1, signal)
    signal = np.where((zscore > -1) & (zscore < -0.5), -1, signal)

    # stoploss
    signal = np.where((zscore > 3), 3, signal)
    signal = np.where((zscore < -3), -3, signal)

    if contract_group.get_contract(strategy_context.s2_symbol): signal = -1 * signal
    print(signal)
    return signal

# check stoploss and target implementation
def pair_trading_rule(contract_group, i, timestamps, indicators, signal, account, strategy_context):
    timestamp = timestamps[i]
    orders = []
    curr_pos = account.position(contract_group, timestamp)
    curr_equity = account.equity(timestamp)
    if(curr_equity<=0):
        return orders
    signal_value = signal[i]
    risk_percent = 1
    pairs_data = pairs_df[(pairs_df['Stock_X']==strategy_context.s1_symbol) & (pairs_df['Stock_Y']==strategy_context.s2_symbol)]
    slope = pairs_data['Slope'].iloc[0]
    order_trigger = SimpleNamespace(trigger = '')

    if(str(contract_group) == 's1'):
        order_multiplier = 1
        # print(strategy_context.s1_symbol)
        lot = int(strategy_context.s1_lot_size)
        # print(lot)
        contract = contract_group.get_contract(strategy_context.s1_symbol)
    else:
        # print(str(contract_group))
        order_multiplier = slope
        lot = int(strategy_context.s2_lot_size)
        # print(lot)
        contract = contract_group.get_contract(strategy_context.s2_symbol)
    if math.isclose(curr_pos, 0):
        if signal_value == 2 or signal_value == -2 :

            order_qty = np.round(order_multiplier * curr_equity * risk_percent / indicators.Close[i] * np.sign(signal_value))
            # order_qty = np.round(order_multiplier * np.sign(signal_value)) * lot
            # print("order_qty = " + str(order_qty))
            # print("signal = " + str(signal_value))
            trigger_price = indicators.Close[i]
            reason_code = pq.ReasonCode.ENTER_LONG if order_qty > 0 else pq.ReasonCode.ENTER_SHORT
            try:
                orders.append(pq.MarketOrder(contract, timestamp, order_qty, reason_code = reason_code))
            except Exception as err:
                # pass
                print("order quantity is 0")

        if signal_value == 3 or signal_value == -3:
            # print("*********************************************888")
            order_qty = np.round(order_multiplier * curr_equity * risk_percent / indicators.Close[i] * np.sign(signal_value))
            # order_qty = np.round(order_multiplier * np.sign(signal_value)) * lot
            # print("order_qty = " + str(order_qty))
            # print("signal = " + str(signal_value))
            # print(signal_value)
            # print(contract)
            # print(order_multiplier * curr_equity * risk_percent / indicators.Close[i] * np.sign(signal_value) * -1)
            trigger_price = indicators.Close[i]
            reason_code = pq.ReasonCode.ENTER_LONG if order_qty > 0 else pq.ReasonCode.ENTER_SHORT
            try:
                orders.append(pq.MarketOrder(contract, timestamp, order_qty, reason_code = reason_code))
                print("order made")
                print(timestamp)
            except Exception as err:
                # pass
                print("order quantity is 0")
    else:
        if (curr_pos > 0 and signal_value == 1) or (curr_pos < 0 and signal_value == -1):
            order_qty = -curr_pos
            order_trigger = SimpleNamespace(trigger = 'Target reached')
            reason_code = pq.ReasonCode.EXIT_LONG if order_qty < 0 else pq.ReasonCode.EXIT_SHORT
            orders.append(pq.MarketOrder(contract, timestamp, order_qty, reason_code = reason_code, properties = order_trigger))

        if (curr_pos > 0 and signal_value == 3) or (curr_pos < 0 and signal_value == -3):
            order_qty = -curr_pos
            order_trigger = SimpleNamespace(trigger = 'Stoploss reached')
            reason_code = pq.ReasonCode.EXIT_LONG if order_qty < 0 else pq.ReasonCode.EXIT_SHORT
            orders.append(pq.MarketOrder(contract, timestamp, order_qty, reason_code = reason_code, properties = order_trigger))
    return orders


def market_simulator(orders, i, timestamps, indicators, signals, strategy_context):
    trades = []
    timestamp = timestamps[i]
    timestamp_date = str(timestamp)[:10]
    # today_date = str(datetime.today()-relativedelta(days = 3))[:10]
    today_date = str(datetime.today())[:10]
    # print(timestamp)
    # print(today_date)
    try:
        for order in orders:
            if(timestamp_date == today_date):
                today_trades.append(order)
            trade_price = np.nan
            contract_group = order.contract.contract_group
            ind = indicators[contract_group]
            o, h, l, c = ind.Open[i], ind.High[i], ind.Low[i], ind.Close[i]
            if isinstance(order, pq.MarketOrder):
                trade_price = 0.5 * (o + h) if order.qty > 0 else 0.5 * (o + l)
            else:
                raise Exception(f'unexpected order type: {order}')
            if np.isnan(trade_price): continue
            trade = pq.Trade(order.contract, order, timestamp, order.qty, trade_price, commission = 0, fee = 0)
            order.status = 'filled'
            trades.append(trade)
            print(str(order) + " trade_price: " + str(trade_price) )

            # print(str(timestamp)[:10])

    except:
        pass
    return trades


def get_price(contract, timestamps, i, strategy_context):
    # symbol = contract.symbol
    if contract.symbol == strategy_context.s1_symbol:
        return strategy_context.s1_price[i]
    elif contract.symbol == strategy_context.s2_symbol:
        return strategy_context.s2_price[i]
    raise Exception(f'Unknown symbol: {contract.symbol}')


def build_strategy(pair, s1_contract_group, s2_contract_group):
    # print("inside")
    end_date = date.today() + relativedelta(days = 1)
    start_date = end_date - relativedelta(years = 2)
    s1_prices = pd.read_csv("stock_data/" + pair[0] + "_" + str(start_date) + "_" + str(end_date) + ".csv")
    s2_prices = pd.read_csv("stock_data/" + pair[1] + "_" + str(start_date) + "_" + str(end_date) + ".csv")
    residuals_df = pd.read_csv('pair_trading_data/' + pair[0] + "_" + pair[1] + ".csv") # read according to the correct order. This is test
    residuals = residuals_df['Residuals']
    timestamps = pd.to_datetime(residuals_df['Date'])
    timestamps = timestamps.values
    # print(timestamps)
    # pair_z_score = zscore_indicator(None, None,SimpleNamespace(residuals = residuals), None)
    # pair_z_score_df = pd.DataFrame(pq.TimeSeries('residuals', timestamps, residuals))
    # print(pair_z_score_df)

    # print([pq.TimeSeries('residuals', timestamps, residuals)])
    # residual_subplot = pq.Subplot([pq.TimeSeries('residuals', timestamps, residuals)], ylabel = 'Ratio')
    # pair_z_score_df.plot(legend = False)
    # zscore_subplot = pq.Subplot([pq.TimeSeries('zscore', timestamps, pair_z_score)], ylabel = 'ZScore')
    # signal = pair_strategy_signal(None, timestamps, SimpleNamespace(zscore = pair_z_score), None, None)
    # signal_subplot = pq.Subplot([pq.TimeSeries('signal', timestamps, signal)], ylabel = 'Signal')
    # plot = pq.Plot([residual_subplot, zscore_subplot, signal_subplot], title = 'temp')
    # plot.show()
    # print(type(pair[0]))
    market_lots = pd.read_csv('fo_mktlots.csv')
    # 3 for septermber month
    try:
        s1_lot_size = market_lots[market_lots['SYMBOL'] == pair[0]].iloc[0, 3]
        s2_lot_size = market_lots[market_lots['SYMBOL'] == pair[1]].iloc[0, 3]
    except:
        s1_lot_size = 100
        s2_lot_size = 100
    # print((s1_lot_size))

    strategy_context = SimpleNamespace(s1_symbol = pair[0], s1_price = s1_prices.Close.values, s1_lot_size = s1_lot_size, s2_symbol = pair[1], s2_price = s2_prices.Close.values, s2_lot_size = s2_lot_size)
    strategy = pq.Strategy(timestamps, [s1_contract_group, s2_contract_group], get_price, trade_lag = 0, strategy_context = strategy_context)
    for tup in [(s1_contract_group, s1_prices), (s2_contract_group, s2_prices)]:
        for column in ['Open', 'High', 'Low', 'Close']:
            strategy.add_indicator(column, tup[1][column].values, contract_groups = [tup[0]])


    strategy.add_indicator('residuals', residuals)
    strategy.add_indicator('zscore', zscore_indicator, depends_on = ['residuals'])
    strategy.add_signal('pair_strategy_signal', pair_strategy_signal, depends_on_indicators = ['zscore'])
    strategy.add_rule('pair_trading_rule', pair_trading_rule, signal_name = 'pair_strategy_signal', sig_true_values = [-3, -2, -1, 1, 2, 3])
    strategy.add_market_sim(market_simulator)
    return strategy


def pair_trading_strategy():
    global pairs_df
    global today_trades
    pairs_df = pd.read_csv('pair_trading_data/pairs.csv')
    # pairs_df = pd.read_csv('temp_pairs.csv')
    # portfolio = pq.Portfolio()
    today_trades = []
    for index, row in pairs_df.iterrows():
        portfolio = pq.Portfolio()
        pq.ContractGroup.clear()
        pq.Contract.clear()
        # portfolio = pq.Portfolio()
        s1_contract_group = pq.ContractGroup.create('s1')
        s2_contract_group = pq.ContractGroup.create('s2')

        # print(index)
        stock_x = row['Stock_X']
        stock_y = row['Stock_Y']
        p_value = row['P-Value from ADF test']
        std_err_residuals = row['std_error_of_residuals']
        slope = row['Slope']
        intercept = row['Intercept']
        pair = [stock_x, stock_y]
        # global g_pair
        # g_pair = pair
        print((pair))
        # contract = contract_group.get_contract(g_pair[0])
        symbol_1_contract = s1_contract_group.get_contract(pair[0])
        if symbol_1_contract is None:
            symbol_1_contract = pq.Contract.create(pair[0], s1_contract_group)
            # print("contract created for " + str(pair[0]))

        symbol_2_contract = s2_contract_group.get_contract(pair[1])
        if symbol_2_contract is None:
            symbol_2_contract = pq.Contract.create(pair[1], s2_contract_group)
            # print("contract created for " + str(pair[1]))

        strategy = build_strategy(pair, s1_contract_group, s2_contract_group)
        strategy_name = 'pair_strategy_' + str(pair[0]) + "_" + str(pair[1])
        # print(symbol_1_contract.contracts_by_symbol())
        portfolio.add_strategy(strategy_name, strategy)
        # pq.Contract.clear()
        # print(s1_contract_group.get_contract(pair[0]))
        # symbol_1_contract.clear()
        # symbol_2_contract.clear()

        # pq.ContractGroup.clear()
        portfolio.run()
    print(today_trades)
    # with open('pair_trades_for_today.csv', 'w') as out_file:
    #     for element in today_trades:
    #         out_file.write(str(element))
    #         out_file.write("\n")

    today_trades_df = pd.DataFrame(today_trades, columns = ['Pair Trades'])
    return today_trades_df


    # portfolio.evaluate_returns()

    # strategy.plot(primary_indicators = ['Close'], secondary_indicators = ['zscore'])
    # portfolio.evaluate_returns()
    # returns_df = portfolio.df_pnl()
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(portfolio.df_returns())
