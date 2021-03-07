import trendet
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# from io import StringIO
# import StringIO
import pandas as pd
import io
from datetime import datetime

# written differently then plot function because it needs to be calculated for all
# stocks while plotting is only for specific plots
def find_trends(data_df):
    print(data_df)
    res = trendet.identify_df_trends(df=data_df, column='Close', window_size=3, identify='up')
    if 'Up Trend' not in res:
        res['Up Trend'] = np.nan
    else:
        print("*****************")
    res = trendet.idres = trendet.identify_df_trends(df=data_df, column='Close', window_size=3, identify='up')
    if 'Up Trend' not in res:
        res['Up Trend'] = np.nan
    else:
        print("*****************")
    res = trendet.identify_df_trends(df=res, column='Close',window_size=3, identify='down')
    res.reset_index(inplace=True)
    res_dict = res.groupby('Date')[['Up Trend','Down Trend']].apply(lambda x: x.to_dict('records')[0]).to_dict()

    return res_dict


def plot_trends(data_df):
    res = trendet.identify_df_trends(df=data_df, column='Close', window_size=3, identify='up')
    if 'Up Trend' not in res:
        res['Up Trend'] = np.nan
    else:
        print("*****************")
    res = trendet.identify_df_trends(df=res, column='Close',window_size=3, identify='down')
    if 'Down Trend' not in res:
        res['Down Trend'] = np.nan
    else:
        print("*****************")
    res.reset_index(inplace=True)
    # res.set_index("Date", inplace = True)
    # print(res.groupby('Date')[['Up Trend','Down Trend']])
    res_dict = res.groupby('Date')[['Up Trend','Down Trend']].apply(lambda x: x.to_dict('records')[0]).to_dict()

    with plt.style.context('seaborn-paper'):
        plt.figure(figsize=(10, 5))
        ax = sns.lineplot(x=res['Date'], y=res['Close'])
        labels = res['Up Trend'].dropna().unique().tolist()

        for label in labels:
            sns.lineplot(x=res[res['Up Trend'] == label]['Date'],
                         y=res[res['Up Trend'] == label]['Close'],
                         color='green')

            ax.axvspan(res[res['Up Trend'] == label]['Date'].iloc[0],
                       res[res['Up Trend'] == label]['Date'].iloc[-1],
                       alpha=0.2,
                       color='green')

        labels = res['Down Trend'].dropna().unique().tolist()
        for label in labels:
            sns.lineplot(x=res[res['Down Trend'] == label]['Date'],
                         y=res[res['Down Trend'] == label]['Close'],
                         color='red')

            ax.axvspan(res[res['Down Trend'] == label]['Date'].iloc[0],
                       res[res['Down Trend'] == label]['Date'].iloc[-1],
                       alpha=0.2,
                       color='red')

        # plt.show()
        symbol = data_df['Symbol'].unique()[0]
        start_day = int(data_df['Date'].iloc[0][8:])
        # print(start_date)
        xticks_list = [*range(0, data_df.shape[0], 30)]
        # start_date =
        # dates_list = pd.date_range(data_df['Date'].iloc[0], data_df['Date'].iloc[-1], freq = 'M').tolist()
        # dates_list = [datetime.strftime(date, '%Y-%m-%d') for date in dates_list]
        dates_list = data_df.groupby('Date').groups.keys()
        # print(dates_list)
        plt.xticks(xticks_list)
        # for ind, label in enumerate(plt.get_xticklabels()):
        #     if ind % 10 == 0:  # every 10th label is kept
        #         label.set_visible(True)
        #     else:
        #         label.set_visible(False)
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='PNG')
        bytes_image.seek(0)

        # plt.savefig('charts/' + symbol + '.png')
    return bytes_image


