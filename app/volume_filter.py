import talib
import numpy


def volume_screener(volumes, date):
    SMA_volume = talib.SMA(volumes, timeperiod=20)
    # since it is a 20 day SMA, it won't give anything for first 20 days. it will give values only after 20 days
    # volume_flag = []

    date_crit_vol = {}
    i = 0
    while i < len(date):
        crit_vol = {}
        if SMA_volume[i] < volumes[i]:
            volume_pct = (volumes[i] - SMA_volume[i]) / SMA_volume[i]
            crit_vol[str(volumes[i])] = volume_pct
        else:
            crit_vol[str(volumes[i])] = 0

        date_crit_vol[date[i]] = crit_vol
        i = i + 1
    return date_crit_vol
