import trendln


# import yfinance as yf

# tick = yf.Ticker('^GSPC')
# hist = tick.history(period = 'max', rounding = True)
# print(type(tick))yfinance.ticker.Ticker object
# print(type(hist))pandas dataframe
# print(hist)

# h = hist[-1000:].Close
# print(type(h))

def sup_res_calculator(h, date):
    # print(date)
    # h = h[-253:]
    # print(h)
    # date = date[-253:]
    # print(date)
    (miniIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(
        h,
        extmethod=trendln.METHOD_NUMDIFF,
        method=trendln.METHOD_NSQUREDLOGN,
        window=125,
        errpct=0.005,
        sortError=False,
        accuracy=2)

    index_count = len(h)
    slope_support = pmin[0]
    intercept_support = pmin[1]
    slope_resistance = pmax[0]
    intercept_resistance = pmax[1]
    S_and_R_global = []

    i = 0
    while (i < index_count):
        S_and_R_local = {}
        sup = slope_support * i + intercept_support
        S_and_R_local['Support'] = sup
        res = slope_resistance * i + intercept_resistance
        S_and_R_local['Resistance'] = res
        S_and_R_global.append(S_and_R_local)
        i = i + 1

    support_date_dict = dict(zip(date, S_and_R_global))

    fig = trendln.plot_support_resistance(h,  # as per h for calc_support_resistance
                                          xformatter=None,
                                          # x-axis data formatter turning numeric indexes to display output
                                          # e.g. ticker.FuncFormatter(func) otherwise just display numeric indexes
                                          numbest=3,  # number of best support and best resistance lines to display
                                          fromwindows=False,
                                          # draw numbest best from each window, otherwise draw numbest across whole range
                                          pctbound=0.1,
                                          # bound trend line based on this maximum percentage of the data range above the high or below the low
                                          extmethod=trendln.METHOD_NUMDIFF,
                                          method=trendln.METHOD_NSQUREDLOGN,
                                          window=125,
                                          errpct=0.005,
                                          # hough_prob_iter=10,
                                          sortError=False,
                                          accuracy=2)

    fig.savefig('suppress.svg', format='svg')
    # print(support_date_dict)
    return support_date_dict
