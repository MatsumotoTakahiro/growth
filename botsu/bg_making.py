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
    print('Usage: python bg_making.py <pre_fitsfile> <fitsfile> <post_fitsfile> <adcchannel> <start_time> <end_time>(%Y/%m/%d %H:%M:%S) <event_name>')
    quit()
    
#input
pre_filename = argv[1]
filename = argv[2]
post_filename = argv[3]
adcchannel = int(argv[4])
start_time = datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S').timestamp()
end_time = datetime.strptime(argv[6], '%Y/%m/%d %H:%M:%S').timestamp()
event_name = argv[7]

#read
pre_evt = fits.getdata(pre_filename, 1, header=True)
pre_data = pd.DataFrame(np.array(pre_evt[0]).byteswap().newbyteorder())
pre_data = pre_data[(pre_data.boardIndexAndChannel.astype('int') == adcchannel) & (pre_data.unixTime > start_time-1800)].reset_index(drop=True)
pre_header = pre_evt[1]

evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data1 = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.unixTime < start_time)].reset_index(drop=True)
data2 = data[(data.boardIndexAndChannel.astype('int') == adcchannel) &  (data.unixTime > end_time)].reset_index(drop=True)
header = evt[1]

post_evt = fits.getdata(post_filename, 1, header=True)
post_data = pd.DataFrame(np.array(post_evt[0]).byteswap().newbyteorder())
post_data = post_data[(post_data.boardIndexAndChannel.astype('int') == adcchannel) & (post_data.unixTime < end_time+1800)].reset_index(drop=True)
post_header = post_evt[1]

#pi
bin_number = 2048
print('ok')
pre_hist = np.histogram(pre_data.energy, bins=bin_number, range=(40, 41000))
hist1 = np.histogram(data1.energy, bins=bin_number, range=(40, 41000))
hist2 = np.histogram(data2.energy, bins=bin_number, range=(40, 41000))
post_hist = np.histogram(post_data.energy, bins=bin_number, range=(40, 41000))
channel = fits.Column(name='CHANNEL', array=np.arange(2048), format='J')
counts = fits.Column(name='COUNTS', array=pre_hist[0]+hist1[0]+hist2[0]+post_hist[0], format='J')
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
spectrum.header.append(('EXPOSURE',3600.0,'exposure (in seconds)'))
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
spectrum.header.append(('EVENTDAT',datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S').strftime('%Y%m%d'),'event date (JST)'))
spectrum.header.append(('EVENTNAM',event_name,'event name'))

#output
hdul = fits.HDUList([primary_hdu, spectrum])
hdul.writeto('{}_bg.pi'.format(event_name), overwrite=True)