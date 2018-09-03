#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
from array import array
from datetime import datetime

#definition
def near(series, value):
    if abs(series[series.searchsorted(value)] - value) > abs(series[series.searchsorted(value)-1] - value):
        return series[series.searchsorted(value)-1]
    else:
        return series[series.searchsorted(value)]

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python rain_integral.py <xrain> <ido_kenshutsuki> <keido_kenshutsuki> <start_time> <end_time>(%Y-%m-%d %H:%M:%S.%f)')
    quit()

xrain = argv[1]
ido_kenshutsuki = float(argv[2])
keido_kenshutsuki = float(argv[3])
start_time = datetime.strptime(argv[4], '%Y-%m-%d %H:%M:%S.%f').timestamp()
end_time = datetime.strptime(argv[5], '%Y-%m-%d %H:%M:%S.%f').timestamp()


#read
xrain_data = pd.read_csv(xrain)
ido_series = np.sort(xrain_data.ido.unique())
keido_series = np.sort(xrain_data.keido.unique())
ido_kenshutsuki_near = near(ido_series, ido_kenshutsuki)
keido_kenshutsuki_near = near(keido_series, keido_kenshutsuki)
rainfall = xrain_data[(xrain_data.ido == ido_kenshutsuki_near) & (xrain_data.keido == keido_kenshutsuki_near)].sort_values('time').reset_index()

#parameter
T = rainfall.time[2] - rainfall.time[1]
print(T)
t1_index = rainfall.time.searchsorted(start_time)
tn_index = rainfall.time.searchsorted(end_time) - 1
print(t1_index, tn_index)
t1_index = t1_index[0]
tn_index = tn_index[0]
event_rainfall = rainfall.iloc[[t1_index,tn_index+1]].reset_index()
print(rainfall[t1_index-1:tn_index+1])

#integral
s1 = rainfall.rain[t1_index] + (rainfall.time[t1_index] - start_time) * (rainfall.rain[t1_index-1] - rainfall.rain[t1_index]) / T
s2 = (2*event_rainfall.rain.sum() - rainfall.rain[t1_index] - rainfall.rain[tn_index])* T /2
s3 = rainfall.rain[tn_index] + (end_time - rainfall.time[tn_index]) * (rainfall.rain[tn_index+1] - rainfall.rain[tn_index]) / T
s_sum = (s1 + s2 + s3) / 3600

#output
print('integrated rainfall is {}'.format(s_sum))