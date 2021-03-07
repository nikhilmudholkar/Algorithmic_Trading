import pandas as pd
import numpy as np
# from mpl_finance import candlestick2_ohlc
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.transforms as transforms
# import finplot as fplt
import matplotlib.dates as mpdates
import matplotlib.pyplot as plt
import io


def isSupport(df, i):
    support = df['Low'][i] < df['Low'][i - 1] and df['Low'][i] < df['Low'][i + 1] and df['Low'][i + 1] < df['Low'][
        i + 2] and df['Low'][i - 1] < df['Low'][i - 2]
    return support


def isResistance(df, i):
    resistance = df['High'][i] > df['High'][i - 1] and df['High'][i] > df['High'][i + 1] and df['High'][i + 1] > \
                 df['High'][i + 2] and df['High'][i - 1] > df['High'][i - 2]
    return resistance


def isFarFromLevel(l, s, levels):
    return np.sum([abs(l - x) < s for x in levels]) == 0


def SandR_calc(stock_data):
    # print(stock_data)
    # stock_data['Date'] = pd.to_datetime(stock_data.index)
    # stock_data['Date'] = stock_data['Date'].apply(mpl_dates.date2num)
    data_df = stock_data.loc[:, ['Open', 'High', 'Low', 'Close']]
    levels = []
    s = np.mean(data_df['High'] - data_df['Low'])
    for i in range(2, data_df.shape[0] - 2):
        if isSupport(data_df, i):
            l = data_df['Low'][i]
            if isFarFromLevel(l, s, levels):
                levels.append((i, l))

        elif isResistance(data_df, i):
            l = data_df['High'][i]
            if isFarFromLevel(l, s, levels):
                levels.append((i, l))

    # plot_all(stock_data, levels)
    levels_list = [level[1] for level in levels]
    print(levels_list)
    return levels_list, levels


def plot_all(data_df, levels):
    # stock_data = data_df.to_numpy()
    stock_data = data_df[['Date', 'Open', 'High',
                          'Low', 'Close']]
    # print(stock_data)
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    stock_data['Date'] = stock_data['Date'].map(mpdates.date2num)
    fig, ax = plt.subplots()
    candlestick_ohlc(ax, stock_data.values, width = 0.6, colorup='green', colordown='red', alpha = 0.8)
    ax.grid(True)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')

    plt.title('Prices For the Period 01-07-2020 to 15-07-2020')
    date_format = mpdates.DateFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    # fig.tight_layout()
    trans = transforms.blended_transform_factory(ax.get_yticklabels()[0].get_transform(), ax.transData)
    ax.yaxis.tick_right()
    for level in levels:
        plt.hlines(level[1], xmin=stock_data['Date'][level[0]], xmax=max(stock_data['Date']), colors='blue')
        ax.text(1.1,level[1], "{:.0f}".format(level[1]), color="red", transform=trans, ha="right", va="center",fontsize=8)
    # ax.yaxis.tick_right()
    # fig.show()
    plt.figure(dpi=256, figsize=(20,10))
    bytes_image = io.BytesIO()
    fig.savefig(bytes_image, format='PNG')
    bytes_image.seek(0)
    return bytes_image


