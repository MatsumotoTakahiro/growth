#! /usr/local/var/pyenv/shims/python

import sys
import numpy as np
from astropy.io import fits

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python fits_dump.py <fitsfile> <adcchannel> ')
    quit()

filename = argv[1]
adcchannel=int(argv[2])

print('RowNumber, timeTag, triggerCount, phaMax')

evt = fits.open(filename, uint=True)
event_data=evt[1].data

for i in range(3):
    string = '{}\t{}\t{}\t{}\n'.format(i,event_data.timeTag[i],event_data.triggerCount[i]+32768,event_data.phaMax[i]+32768)
    print(string)
print(type(event_data.phaMax[0]))
