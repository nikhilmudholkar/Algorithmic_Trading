import datetime

with open('/home/parallax/algo_trading/app/dateInfo.txt','a') as outFile:
    outFile.write('\n' + str(datetime.datetime.now()))
