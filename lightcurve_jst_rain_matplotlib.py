#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
from array import array
from datetime import datetime
import matplotlib.pyplot as plt

#definition
def near(series, value):
    if abs(series[series.searchsorted(value)] - value) > abs(series[series.searchsorted(value)-1] - value):
        return series[series.searchsorted(value)-1]
    else:
        return series[series.searchsorted(value)]

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python lightcurve_jst_rain_30min.py <fitsfile> <adcchannel> <binwidth (sec)> <energylimitslow (MeV)> <energylimitshigh (MeV)> <xrain> <ido_kenshutsuki> <keido_kenshutsuki> <fitsfile2> <center_time>(%Y-%m-%d %H:%M:%S.%f)')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimits_low=float(argv[4]) * 1000
energylimits_high=float(argv[5]) * 1000
xrain = argv[6]
ido_kenshutsuki = float(argv[7])
keido_kenshutsuki = float(argv[8])
filename2 = argv[9]
center_time = datetime.strptime(argv[10], '%Y-%m-%d %H:%M:%S.%f').timestamp()

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high)].reset_index(drop=True)
header = evt[1]

evt2 = fits.getdata(filename2, 1, header=True)
data2 = pd.DataFrame(np.array(evt2[0]).byteswap().newbyteorder())
data2 = data2[(data2.boardIndexAndChannel.astype('int') == adcchannel) & (data2.energy > energylimits_low) & (data2.energy < energylimits_high)].reset_index(drop=True)

merged_data = pd.concat([data, data2], ignore_index=True)
merged_data = merged_data[((merged_data.unixTime > center_time-900.0) & (merged_data.unixTime < center_time+900.0))].reset_index(drop=True)

xrain_data = pd.read_csv(xrain)
ido_series = np.sort(xrain_data.ido.unique())
keido_series = np.sort(xrain_data.keido.unique())
ido_kenshutsuki_near = near(ido_series, ido_kenshutsuki)
keido_kenshutsuki_near = near(keido_series, keido_kenshutsuki)
rainfall = xrain_data[(xrain_data.ido == ido_kenshutsuki_near) & (xrain_data.keido == keido_kenshutsuki_near)].sort_values('time').reset_index()

#hist
observation_time = merged_data.unixTime[-1:] - merged_data.unixTime[0]
bin_number = math.floor(observation_time / binwidth)
hist = np.histogram(merged_data.unixTime, bins=bin_number)
    
timearray = np.delete(hist[1]+0.5*binwidth, -1)
time_from_max = timearray - center_time
scaled_count = hist[0] / binwidth

#plot
fig, ax1 = plt.subplots()
ax1.errorbar(time_from_max, scaled_count, yerr=np.sqrt(hist[0])/binwidth, fmt='k.', capsize=4.0, label='count rate')
ax1.set_ylabel('Count Rate (count/sec)')
ax1.set_xlabel('Second from max radiation {}'.format(argv[10]))

ax2 = ax1.twinx()
ax2.plot(rainfall.time-center_time, rainfall.rain, 'bo', label='precipitation')
ax2.set_ylim([0,10.0])
ax2.set_ylabel('Precipitation (mm/h)')

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc='upper right')

plt.savefig('lightcurve__{}sec_{}-{}MeV_withRain.png'.format(argv[3], argv[4], argv[5]))
