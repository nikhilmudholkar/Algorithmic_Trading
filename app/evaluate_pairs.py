import pandas as pd
import csv
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sector_wise_pairs_generator import pairs_generator
from linear_regression import linear_regression
from statsmodels.tsa.stattools import adfuller


class StationarityTests:
    def __init__(self, significance=.05):
        self.SignificanceLevel = significance
        self.pValue = None
        self.isStationary = None

    def ADF_Stationarity_Test(self, timeseries, printResults = True):
        #Dickey-Fuller test:
        adfTest = adfuller(timeseries, autolag='AIC')
        self.pValue = adfTest[1]
        if (self.pValue<self.SignificanceLevel):
            self.isStationary = True
        else:
            self.isStationary = False
        if printResults:
            dfResults = pd.Series(adfTest[0:4], index=['ADF Test Statistic','P-Value','# Lags Used','# Observations Used'])
            #Add Critical Values
            for key,value in adfTest[4].items():
                dfResults['Critical Value (%s)'%key] = value
            print('Augmented Dickey-Fuller Test Results:')
            print(dfResults)



# pairs_list = [['HDFCBANK', 'ICICIBANK'], ['INFY', 'TCS'], ['HDFCBANK', 'KOTAKBANK'], ['KOTAKBANK', 'ICICIBANK']]
def evaluate_pairs(pairs_list):
    end_date = date.today() + relativedelta(days = 1)
    start_date = end_date - relativedelta(years = 2)
    col_names = ['Stock_X', 'Stock_Y', 'Intercept', 'Slope', 'P-Value from ADF test', 'std_error_of_residuals', 'latest_residual', 'std_err_zscore']
    pairs_df = pd.DataFrame(columns = col_names)


    for pair in pairs_list:
        residuals_df = pd.DataFrame(columns = ['Date', 'Residuals'])
        # print(pair)
        stock_1 = pair[0]
        # print(stock_1)
        stock_2 = pair[1]
        # print(stock_2)

        df_stock_1 = pd.read_csv("stock_data/" + stock_1 + "_" + str(start_date) + "_" + str(end_date) + ".csv")
        df_stock_2 = pd.read_csv("stock_data/" + stock_2 + "_" + str(start_date) + "_" + str(end_date) + ".csv")
        # df_stock_1.drop(df_stock_1.tail(1).index,inplace=True)
        # df_stock_2.drop(df_stock_2.tail(1).index,inplace=True)
        # merged_df = pd.concat([df_stock_1['Date'], df_stock_1['Close'], df_stock_2['Close']], axis = 1, keys=['Date', 'Close_stock_1', 'Close_stock_2'])
        try:
            residuals_1, error_ratio_1, slope_1, intercept_1, std_err_residuals_1 = linear_regression(df_stock_1, df_stock_2)
            residuals_2, error_ratio_2, slope_2, intercept_2, std_err_residuals_2 = linear_regression(df_stock_2, df_stock_1)
        except Exception as err:
            print(err)
        # print("straight = " + str(error_ratio_1))
        # print("reverse = " + str(error_ratio_2))
        date_series = df_stock_1['Date']
        # print(type(date_df))

        if(error_ratio_1<error_ratio_2):
            # print(True)
            stock_x = stock_1
            stock_y = stock_2
            residuals = residuals_1
            error_ratio = error_ratio_1
            slope = slope_1
            intercept = intercept_1
            std_err_residuals = std_err_residuals_1
        else:
            stock_x = stock_2
            stock_y = stock_1
            residuals = residuals_2
            error_ratio = error_ratio_2
            slope = slope_2
            intercept = intercept_2
            std_err_residuals = std_err_residuals_2

        std_err_zscore = round(residuals[-1]/std_err_residuals,2)
        sTest = StationarityTests()
        sTest.ADF_Stationarity_Test(residuals, printResults = False)
        # print("Is the time series stationary? {0}".format(sTest.isStationary))
        pValue = sTest.pValue
        # print(residuals)
        # slope filters because I don't have enough money
        if(sTest.isStationary == True and slope > 0):
            temp_list = [stock_x, stock_y, intercept, slope, sTest.pValue, std_err_residuals, residuals[-1], std_err_zscore]
            pairs_df.loc[len(pairs_df)] = temp_list
            pairs_df.to_csv('pair_trading_data/pairs.csv', index = False)
        else:
            print("pair residuals are not stationary")

        residuals = pd.Series(residuals, name = 'Residuals')
        residuals_df = pd.concat([date_series, residuals], axis = 1)
        residuals_df.to_csv('pair_trading_data/' + stock_x + "_" + stock_y + ".csv", index = False)
        # print(residuals_df)
    return pairs_df



pairs_list = [['TATASTEEL', 'JSWSTEEL']]
# evaluate_pairs(pairs_list)
