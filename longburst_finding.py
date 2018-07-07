#! /usr/local/var/pyenv/shims/python

import sys
import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
#from tqdm import tqdm

if __name__ == '__main__':
    
    #argv
    argv = sys.argv
    fitsfile = argv[1]
    adcchannel=int(argv[2])
    bin_num = int(argv[3])
    energylimitslow=int(argv[4])
    energylimitshigh=int(argv[5])

    #input
    evt = fits.open(fitsfile)
    data = pd.DataFrame(evt[1].data)
    timetag = data.timeTag[(adcchannel==data.boardIndexAndChannel) & (data.phaMax>=energylimitslow) & (data.phaMax<energylimitshigh)].reset_index(drop=True)
    
    eventtime = np.zeros(len(timetag))
    eventtime[0] = timetag[0]

    for i in range(1,len(timetag)):
        eventtime[i] = timetag[i]
        if eventtime[i] == 0:
            eventtime[i] = eventtime[i-1]
        elif eventtime[i] < eventtime[i-1] :
            eventtime[i] += 2**40
        else:
            pass

    eventtime = eventtime / 1e8
    
    hist = np.histogram(eventtime, bins=bin_num)
    crate = hist[0]
    mean = np.mean(crate)
    std = np.sqrt(mean)
    crate[crate==0] = np.mean(crate)
    
    if np.where(crate > mean + 6*std, 1, 0).sum() > 0:
        print(fitsfile)