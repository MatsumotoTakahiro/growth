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
        data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high)].reset_index(drop=True)
                
        #hist
        bin_number = math.floor(3600 / (2*binwidth))
        hist = np.histogram(data.unixTime, bins=bin_number)
        
        #write
        for j in range(bin_number):
            string = "{},{},{}\n".format(hist[1][j]+0.5*binwidth, hist[0][j], np.sqrt(hist[0][j]))
            f.write(string)
            
        