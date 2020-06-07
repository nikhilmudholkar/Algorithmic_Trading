import os
import json
import logging
import pickle
from datetime import date, datetime
from decimal import Decimal
from TA_screener import TA_screener
from checklist import checklist
from flask import Flask, request, jsonify, session
from flask import render_template
from data_downloader import data_downloader
from stoploss_target import stoploss, target

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
index_template = """
    <a target="_blank" href="/backtest.json"><h4>Backtest</h4></a>
    <a target="_blank" href="/download_historic_data"><h4>Download historic data</h4></a>
    <a target="_blanl" href="/technical_analysis_screener.html"><h4> Technical Analysis Screener</h4></a>
    <a target="_blanl" href="/dummy_end_point.json"><h4> Dummy End Point</h4></a>
    """

status_template = """<h1>{status}</h1>
"""

@app.route("/")
def index():
    return index_template

@app.route("/technical_analysis_screener.html")
def TA_Screener():
    logger.debug("Inside TA Screener")
    TA_screener()
    with open('TA_screener_output.json') as json_file:
        TA_results = json.load(json_file)
    trades = checklist(TA_results)
    stoploss_dict = stoploss(trades)
    target_dict = target(trades)


    return render_template('technical_analysis_screener.html',
                            trades = trades,
                            stoploss_dict = stoploss_dict,
                            target_dict = target_dict,
                            title = 'TA_signal_generator')

@app.route("/download_historic_data")
def data_download():
    logger.debug("inside data download function")
    status = data_downloader()
    if(status == 'success'):
        return status_template.format(status = status)
    else:
        return status_template.format(status = 'fail')

if __name__ == "__main__":
    # TA_screener(logger)
    logging.info("Starting server: http://{host}:{port}".format(host=HOST, port=PORT))
    app.run(host= '0.0.0.0')
