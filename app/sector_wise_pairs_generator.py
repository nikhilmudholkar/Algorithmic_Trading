import pandas as pd
import csv


def pairs_generator(filename):
    nifty_100 = pd.read_csv(filename)
    wishlist = pd.read_csv('wishlist.csv', header = None)
    wishlist =list(wishlist.iloc[:,0])
    # print((wishlist))
    sector_list = nifty_100['Industry'].unique()
    pairs_list = []
    for industry in sector_list:
        filtered_df = nifty_100.loc[nifty_100['Industry'] == industry]
        symbol_list = list(set(list(filtered_df['Symbol'])) & set(wishlist))
        temp_list = [[symbol_list[i],symbol_list[j]] for i in range(len(symbol_list)) for j in range(i+1, len(symbol_list))]
        # print(type(temp_list))
        for element in temp_list:
            # if element in wishlist:
                pairs_list.append(element)
        # print((temp_list))

    print(len(pairs_list))
    return pairs_list
