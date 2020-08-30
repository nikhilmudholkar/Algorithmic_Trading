import os
import json
import logging
import pickle
import pandas as pd
from datetime import date, datetime
from decimal import Decimal
from TA_screener import TA_screener
from checklist import checklist
from flask import Flask, request, jsonify, session
from flask import render_template
from data_downloader import data_downloader_stock, data_downloader_FnO_daily, data_downloader_FnO_historical
from calender_spreads import calender_spread_spotter
from stoploss_target import stoploss, target
from calender_spreads_backtest import run_calender_spreads_backtest, calculate_pl
from performance_indicators import sharpe_ratio
from datetime import date, timedelta
from sector_wise_pairs_generator import pairs_generator
from evaluate_pairs import evaluate_pairs

print("successfully starrted")
# logging.basicConfig(filename = "log_file.log",
#                     format = '%(asctime)s %(message)s',
#                     filemode = 'w')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# logger.log("DEBUG")

# Base settings
PORT = 5000
HOST = "127.0.0.1"
serializer = lambda obj: isinstance(obj, (date, datetime, Decimal)) and str(obj)  # noqa

# App
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Templates
status_template = """<h1>{status}</h1>
"""

@app.route("/")
def index():
    # status = data_downloader()
    return render_template('index_template.html',
                            title = 'Pandora\'s Box')

@app.route("/technical_analysis_screener_today.html")
def TA_Screener_today():
    logger.debug("Inside TA Screener")
    TA_screener(1)
    with open('TA_screener_output.json') as json_file:
        TA_results = json.load(json_file)
    # print(TA_results)
    trades = checklist(TA_results)
    stoploss_dict = stoploss(trades)
    target_dict = target(trades)


    return render_template('technical_analysis_screener.html',
                            trades = trades,
                            stoploss_dict = stoploss_dict,
                            target_dict = target_dict,
                            title = 'TA_signal_generator')


@app.route("/technical_analysis_screener_yesterday.html")
def TA_Screener_yesterday():
    logger.debug("Inside TA Screener")
    TA_screener(2)
    with open('TA_screener_output.json') as json_file:
        TA_results = json.load(json_file)
    # print(TA_results)
    trades = checklist(TA_results)
    stoploss_dict = stoploss(trades)
    target_dict = target(trades)


    return render_template('technical_analysis_screener.html',
                            trades = trades,
                            stoploss_dict = stoploss_dict,
                            target_dict = target_dict,
                            title = 'TA_signal_generator')







@app.route("/download_historical_stock_data")
def data_download_stock():
    logger.debug("inside data download function")
    status = data_downloader_stock()
    if(status == 'success'):
        return status_template.format(status = status)
    else:
        return status_template.format(status = 'fail')


@app.route("/download_historical_FnO_data")
def data_download_FnO_historical():
    logger.debug("inside data download function")
    status = data_downloader_FnO_historical(2000)
    if(status == 'success'):
        return status_template.format(status = status)
    else:
        return status_template.format(status = 'fail')

@app.route("/download_daily_FnO_data")
def data_download_FnO_daily():
    logger.debug("inside data download function")
    status = data_downloader_FnO_daily(2)
    if(status == 'success'):
        return status_template.format(status = status)
    else:
        return status_template.format(status = 'fail')


@app.route("/calender_spreads")
def calender_spreads():
    result_df = calender_spread_spotter(0)
    current_date = date.today()
    date_required = current_date - timedelta(0)
    return render_template('df_template.html', date = date_required,  tables=[result_df.to_html(classes='data')], titles=result_df.columns.values)

    # if(status == 'success'):
    #     return status_template.format(status = status)
    # else:
    #     return status_template.format(status = 'fail')


@app.route("/calender_spreads_backtest")
def calender_spreads_backtest():
    # signals_df = run_calender_spreads_backtest()
    calculate_pl()
    trades_df = pd.read_csv('calender_spread_trades.csv')
    sharpe = sharpe_ratio(trades_df)
    return render_template('performance_indicator.html',
                            title = 'Strategy Performance',
                            sharpe_ratio = sharpe)

@app.route("/pairs_list")
def pairs_list_generator():
    current_date = date.today()
    date_required = current_date - timedelta(0)
    pairs_list = pairs_generator('ind_nifty100list.csv')
    pairs_df = evaluate_pairs(pairs_list)
    return render_template('df_template.html', date = date_required,  tables=[pairs_df.to_html(classes='data')], titles=pairs_df.columns.values)







if __name__ == "__main__":
    # TA_screener(logger)
    logging.info("Starting server: http://{host}:{port}".format(host=HOST, port=PORT))
    app.run(host= '0.0.0.0')
