#! /usr/local/var/pyenv/shims/python

import ROOT
import sys
import math
import numpy as np
import pandas as pd
from astropy.io import fits
from datetime import datetime
from datetime import date

argv = sys.argv

#error
if len(argv) < 2:
    print('Usage: python pi_making.py <fitsfile> <adcchannel> <start_time> <end_time>(%Y-%m-%d %H:%M:%S.%f) <event_name> <pi_type>("sr" or "bg")')
    quit()
    
#input
filename = argv[1]
adcchannel = int(argv[2])
start_time = datetime.strptime(argv[3], '%Y-%m-%d %H:%M:%S.%f').timestamp()
end_time = datetime.strptime(argv[4], '%Y-%m-%d %H:%M:%S.%f').timestamp()
event_name = argv[5]
pi_type = argv[6]

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.unixTime > start_time) & (data.unixTime < end_time)].reset_index(drop=True)
header = evt[1]
energy_width = header['BINW_CH{}'.format(adcchannel)]
data['true_energy'] = data.energy + energy_width*np.random.uniform(-0.5, 0.5, size=data.energy.shape)
print('photon_number = {}'.format(len(data.index)))

#pi
bin_number = 2048
hist = np.histogram(data.true_energy, bins=bin_number, range=(40, 41000))
channel = fits.Column(name='CHANNEL', array=np.arange(2048), format='J')
counts = fits.Column(name='COUNTS', array=hist[0], format='J')
spectrum = fits.BinTableHDU.from_columns([channel, counts])
spectrum.name = 'SPECTRUM'

#header
primary_hdu = fits.PrimaryHDU()
spectrum.header.append(('HDUCLASS','OGIP','format conforms to OGIP standard'))
spectrum.header.append(('HDUVERS1','1.2.0   ','Obsolete - included for backwards compatibility'))
spectrum.header.append(('HDUVERS','1.2.0   ','Version of format (OGIP memo OGIP-92-007)'))
spectrum.header.append(('HDUCLAS2','DERIVED ','WARNING This is NOT an OGIP-approved value'))
spectrum.header.append(('HDUCLAS3','COUNT   ','PHA data stored as Counts (not count/s)'))
spectrum.header.append(('TLMIN1',0,'Lowest legal channel number'))
spectrum.header.append(('TLMAX1',2047,'Highest legal channel number'))
spectrum.header.append(('TELESCOP','GROWTH','mission name'))
spectrum.header.append(('INSTRUME',header['DET_ID'],'detector ID'))
spectrum.header.append(('FILTER','NONE    ','filter in use'))
spectrum.header.append(('EXPOSURE',end_time-start_time,'exposure (in seconds)'))
spectrum.header.append(('AREASCAL',1.000000E+00,'area scaling factor'))
spectrum.header.append(('BACKFILE','NONE    ','associated background filename'))
spectrum.header.append(('BACKSCAL',1.000000E+00,'background file scaling factor'))
spectrum.header.append(('CORRFILE','NONE    ','associated correction filename'))
spectrum.header.append(('CORRSCAL',1.000000E+00,'correction file scaling factor'))
spectrum.header.append(('RESPFILE','NONE    ','associated redistrib matrix filename'))
spectrum.header.append(('ANCRFILE','NONE    ','associated ancillary response filename'))
spectrum.header.append(('PHAVERSN','1992a   ','obsolete'))
spectrum.header.append(('DETCHANS',2048,'total number possible channels'))
spectrum.header.append(('CHANTYPE','PI      ','channel type (PHA, PI etc)'))
spectrum.header.append(('POISSERR',True,'Poissonian errors are applicable'))
spectrum.header.append(('SYS_ERR',0,'no systematic error specified'))
spectrum.header.append(('GROUPING',0,'no grouping of the data has been defined'))
spectrum.header.append(('EVENTDAT',datetime.strptime(argv[3], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y%m%d'),'event date (JST)'))
spectrum.header.append(('EVENTNAM',event_name,'event name'))

#output
hdul = fits.HDUList([primary_hdu, spectrum])
hdul.writeto('{}_{}.pi'.format(event_name, pi_type), overwrite=True)