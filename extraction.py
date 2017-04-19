import sys
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from collections import Counter

def valid_read(target_time, gap):
    range_y=target_time
    range_x=range_y-pd.to_timedelta(gap, unit='m')   
    loc_pre=df.loc[range_x:range_y].Global_active_power 
    loc_pre_mean= loc_pre.rolling(window=15).mean()
    loc_pre_mean[15:].plot()
    plot.title(target_time)
    plot.show()

def main( target_time , gap ):
    #抓取時間範圍
    range_y=target_time
    range_x=range_y-pd.to_timedelta(gap, unit='m')    #往前抓取1小時
    loc_pre=df.loc[range_x:range_y].Global_active_power #撈資料
    loc_pre_mean= loc_pre.rolling(window=15).mean()    #計算移動平均
    #print(loc_pre_mean[15:].values)
    #print('===============================')
    min_distance = None
    stamp = None
    #星期為單位比較相似度
    for i in range(1,6,1):
        #1,2,3,4,5
        range_y=target_time-pd.to_timedelta(7*i, unit='d')#抓取前i禮拜資料
        range_x=range_y-pd.to_timedelta(gap, unit='m') #抓取前gap分鐘
        range_time=range_x,range_y
        loc_before = df.loc[range_time[0]:range_time[1]].Global_active_power #抓資料
        #計算移動平均
        loc_before_mean= loc_before.rolling(window=15).mean()
        #print(loc_before_mean[15:].values)
        #計算移動平均的DWT距離
        distance, path = fastdtw(loc_pre_mean[15:].values, loc_before_mean[15:].values, dist=euclidean)
        #print(distance)
        #print('===============================')
        #尋找最小的距離並記錄timestamp        
        if min_distance == None:
            min_distance=distance
            stamp = i*7
        if min_distance >  distance:
            min_distance=distance
            stamp = i*7
    #天為單位比較相似度
    for i in range(1,6,1):
        #1,2,3,4,5
        range_y=target_time-pd.to_timedelta(1*i, unit='d')
        range_x=range_y-pd.to_timedelta(gap, unit='m') 
        range_time=range_x,range_y
        loc_before = df.loc[range_time[0]:range_time[1]].Global_active_power #抓資料
        #計算移動平均
        loc_before_mean= loc_before.rolling(window=15).mean()
        #print(loc_before_mean[15:].values)
        #計算移動平均的DWT距離
        distance, path = fastdtw(loc_pre_mean[15:].values, loc_before_mean[15:].values, dist=euclidean)
        #print(distance)
        #print('===============================')
        if min_distance >  distance:
            min_distance=distance
            stamp = i
    print('==================================')
    print(gap)
    print(min_distance)
    print(stamp)
    return min_distance , stamp

if __name__ == "__main__":
    df=pd.read_csv('D:\Dropbox\paper/dataset/new_record.csv')#讀取資料
    df.index = pd.to_datetime(df['Datetime']) #轉換index，因為從csv讀取無index
    date=format(sys.argv[1])
    time=format(sys.argv[2])
    #gap = 90 #1.5個小時
    target_time=pd.to_datetime(date+' '+time)#轉換時間標籤
    stamp_tmp = []
    distance = []
    for gap in range(30,105,15):
        #30、45、60、75、90
        min_distance , stamp = main(target_time, gap)
        stamp_tmp.append(stamp)
        distance.append(min_distance)
    dictionary=dict(zip(stamp_tmp, distance))
    #fine the most common element in list
    stamp=Counter(stamp_tmp).most_common(1)
    print('最接近的時間: %s 天前' %(stamp[0][0]))
    '''
    是否需要計算平均的距離驗算正確度?
    print('平均距離: %s ' %(stamp))
    '''
    min_target_time=target_time-pd.to_timedelta(stamp , unit='d')
    valid_read(target_time,gap)
    valid_read(min_target_time,gap)
