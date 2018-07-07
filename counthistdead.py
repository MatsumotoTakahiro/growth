#! /usr/local/var/pyenv/shims/python

import os
import sys
import math
import random
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.table import Table

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python counthist.py <dir_name> <adcchannel> <binwidth (sec)> <energylimitslow (MeV)> <energylimitshigh (MeV)> <out_filename>')
    quit()

dirname = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimits_low=float(argv[4]) * 1000
energylimits_high=float(argv[5]) * 1000
out_filename = argv[6]

#file_list
files = os.listdir(dirname)
file_number = len(files)

#output_file
with open(out_filename, 'a') as f:

    for i in range(file_number):
        #read
        evt = Table.read(files[i], hdu=1)
        data = pd.DataFrame(np.array(evt))
        data = data[data.boardIndexAndChannel.astype('int') == adcchannel].reset_index(drop=True)
        
        #hist
        bin_number = math.floor(3600 / (2*binwidth))
        hist = np.histogram(data.unixTime, bins=bin_number)
        
        #trigger_data
        trigger_data = pd.DataFrame({
            'delta_trigger':np.roll(data.triggerCount, -1) - data.triggerCount, 'unix_time':data.unixTime
            })
        data_dead = []
        for j in range(len(trigger_data.index)-1):
            for k in range(trigger_data.delta_trigger[j]-1):
                data_dead.append(random.uniform(trigger_data.unix_time[i], trigger_data.unix_time[i+1]))
        print('{}/{}\t{}'.format(i, file_number, len(data_dead)))
        hist_dead = np.histogram(data_dead, bins=hist[1])
        
        #energy_band        
        data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high)].reset_index(drop=True)
        hist_energy_band = np.histogram(data.unixTime, bins=hist[1])
        
        #write
        for j in range(bin_number):
            if hist[0][j] ==0:
                scale_factor = 1
            else:
                scale_factor = (hist[0][j] + hist_dead[0][j]) / hist[0][j]
            string = "{},{},{}\n".format(hist[1][j]+0.5*binwidth, hist_energy_band[0][j]*scale_factor, np.sqrt(hist_energy_band[0][j])*scale_factor)
            f.write(string)
