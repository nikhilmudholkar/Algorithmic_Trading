import statsmodels.api as sm
import pandas as pd
import csv
import numpy as np


def linear_regression(df_stock_1, df_stock_2):
    # print(df_stock_1)
    # print(df_stock_2)
    X1 = df_stock_1['Close']
    y = list(df_stock_2['Close'])
    X = sm.add_constant(X1)
    # print(X.shape)
    # print(len(y))
    try:
        model = sm.OLS(y, X)
        result = model.fit()
    except Exception as err:
        return err
    std_err_intercept = round(result.bse['const'], 2)
    residuals = np.array(result.resid)
    std_err_residuals = round(residuals.std(), 2)
    error_ratio = round(std_err_intercept/std_err_residuals, 2)
    slope = result.params['Close']
    intercept = result.params['const']
    return residuals, error_ratio, slope, intercept, std_err_residuals
