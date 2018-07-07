#! /usr/local/var/pyenv/shims/python

import os
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python photon_number.py <dataset_name> <binwidth (sec)> <Mean (count/sec)> <Sigma (count/sec)> <Sigma_error (count/sec)> <threshold (sigma)> <center_time>(%Y/%m/%d %H:%M:%S)  <time_window(sec)>')
    quit()

dataset_name = argv[1]
binwidth = float(argv[2])
mean = float(argv[3])
sigma = float(argv[4])
sigma_err = float(argv[5])
threshold = float(argv[6])
center_time = datetime.strptime(argv[7], '%Y/%m/%d %H:%M:%S').timestamp()
time_window = float(argv[8])

#dataset
data = pd.read_csv(dataset_name, names=('time', 'cr', 'err'), dtype={'time':'float64', 'cr':'float64', 'err':'float64'})
evt_data = data[(data.time > center_time-0.5*time_window) & (data.time < center_time+0.5*time_window)].reset_index(drop=True)
evt_data['event_photon'] = evt_data.cr - mean
evt_data['significance'] = evt_data.event_photon / sigma
print(evt_data.significance)

#calculate
photon_number = evt_data[evt_data.significance > threshold].event_photon.sum()
photon_number_err = np.sqrt((evt_data[evt_data.significance > threshold].err ** 2).sum())
event_start = evt_data[evt_data.significance > threshold].time.min()
event_end = evt_data[evt_data.significance > threshold].time.max()
duration = event_end - event_start
duration_err = np.sqrt(2) * binwidth * 0.5
max_significance = evt_data.significance.max()
max_significance_err = max_significance * np.sqrt(evt_data.cr.max()/(evt_data.cr.max() - mean)**2 + (sigma_err/sigma)**2)
max_significance_time = evt_data.time[evt_data.significance.idxmax()]

#output
string = """This event's status
It started at {}.
It ended at {}.
It lasted for {} +/- {} seconds.
Its maximum significance is {} +/- {} at {}.
Its photon number is {} +/- {}.""".format(datetime.fromtimestamp(event_start), datetime.fromtimestamp(event_end), duration, duration_err, max_significance, max_significance_err, datetime.fromtimestamp(max_significance_time), photon_number, photon_number_err)
print(string)

with open('result.txt', 'a') as f:
    f.write(string)