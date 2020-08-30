from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import os
import pandas as pd

def sharpe_ratio(trades_df):
    returns = trades_df['returns']
    risk_free_return = 0.058
    print('mean returns = ' + str(returns.mean()))
    print('std returns ' + str(returns.std()))
    # sharpe = (returns.mean() - risk_free_return)/returns.std()
    sharpe = (returns.mean())/returns.std()
    annulized_sharpe = ((trades_df.shape[0]/5.5)**0.5) * sharpe
    print(trades_df.shape[0])
    return annulized_sharpe
