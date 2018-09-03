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
#post_filename = argv[3]
adcchannel = int(argv[3])
start_time = datetime.strptime(argv[4], '%Y/%m/%d %H:%M:%S').timestamp()
end_time = datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S').timestamp()
event_name = argv[6]

#read
pre_evt = fits.getdata(pre_filename, 1, header=True)
pre_data = pd.DataFrame(np.array(pre_evt[0]).byteswap().newbyteorder())
pre_header = pre_evt[1]

evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
header = evt[1]

#post_evt = fits.getdata(post_filename, 1, header=True)
#post_data = pd.DataFrame(np.array(post_evt[0]).byteswap().newbyteorder())
#post_header = post_evt[1]

merged_data = pd.concat([pre_data, data], ignore_index=True)
sr_data = merged_data[(merged_data.boardIndexAndChannel.astype('int') == adcchannel) & (merged_data.unixTime > start_time) & (merged_data.unixTime < end_time)].reset_index(drop=True)
#bg_data_pre = merged_data[(merged_data.boardIndexAndChannel.astype('int') == adcchannel) & (merged_data.unixTime < start_time) & (merged_data.unixTime > start_time-1800)].reset_index(drop=True)
bg_data_post = merged_data[(merged_data.boardIndexAndChannel.astype('int') == adcchannel) & (merged_data.unixTime > end_time) & (merged_data.unixTime < end_time+1800)].reset_index(drop=True)

#pi
bin_number = 2048
#bg_pre_hist = np.histogram(bg_data_pre.energy, bins=bin_number, range=(40, 41000))
sr_hist = np.histogram(sr_data.energy, bins=bin_number, range=(40, 41000))
bg_post_hist = np.histogram(bg_data_post.energy, bins=bin_number, range=(40, 41000))
channel = fits.Column(name='CHANNEL', array=np.arange(2048), format='J')
sr_counts = fits.Column(name='COUNTS', array=sr_hist[0], format='J')
bg_counts = fits.Column(name='COUNTS', array=bg_post_hist[0], format='J')
sr_spectrum = fits.BinTableHDU.from_columns([channel, sr_counts])
sr_spectrum.name = 'SPECTRUM'
bg_spectrum = fits.BinTableHDU.from_columns([channel, bg_counts])
bg_spectrum.name = 'SPECTRUM'

#sr_header
primary_hdu = fits.PrimaryHDU()
sr_spectrum.header.append(('HDUCLASS','OGIP','format conforms to OGIP standard'))
sr_spectrum.header.append(('HDUVERS1','1.2.0   ','Obsolete - included for backwards compatibility'))
sr_spectrum.header.append(('HDUVERS','1.2.0   ','Version of format (OGIP memo OGIP-92-007)'))
sr_spectrum.header.append(('HDUCLAS2','DERIVED ','WARNING This is NOT an OGIP-approved value'))
sr_spectrum.header.append(('HDUCLAS3','COUNT   ','PHA data stored as Counts (not count/s)'))
sr_spectrum.header.append(('TLMIN1',0,'Lowest legal channel number'))
sr_spectrum.header.append(('TLMAX1',2047,'Highest legal channel number'))
sr_spectrum.header.append(('TELESCOP','GROWTH','mission name'))
sr_spectrum.header.append(('INSTRUME',header['DET_ID'],'detector ID'))
sr_spectrum.header.append(('FILTER','NONE    ','filter in use'))
sr_spectrum.header.append(('EXPOSURE',end_time-start_time,'exposure (in seconds)'))
sr_spectrum.header.append(('AREASCAL',1.000000E+00,'area scaling factor'))
sr_spectrum.header.append(('BACKFILE','NONE    ','associated background filename'))
sr_spectrum.header.append(('BACKSCAL',1.000000E+00,'background file scaling factor'))
sr_spectrum.header.append(('CORRFILE','NONE    ','associated correction filename'))
sr_spectrum.header.append(('CORRSCAL',1.000000E+00,'correction file scaling factor'))
sr_spectrum.header.append(('RESPFILE','NONE    ','associated redistrib matrix filename'))
sr_spectrum.header.append(('ANCRFILE','NONE    ','associated ancillary response filename'))
sr_spectrum.header.append(('PHAVERSN','1992a   ','obsolete'))
sr_spectrum.header.append(('DETCHANS',2048,'total number possible channels'))
sr_spectrum.header.append(('CHANTYPE','PI      ','channel type (PHA, PI etc)'))
sr_spectrum.header.append(('POISSERR',True,'Poissonian errors are applicable'))
sr_spectrum.header.append(('SYS_ERR',0,'no systematic error specified'))
sr_spectrum.header.append(('GROUPING',0,'no grouping of the data has been defined'))
sr_spectrum.header.append(('EVENTDAT',datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S').strftime('%Y%m%d'),'event date (JST)'))
sr_spectrum.header.append(('EVENTNAM',event_name,'event name'))

#sr_output
sr_hdul = fits.HDUList([primary_hdu, sr_spectrum])
sr_hdul.writeto('{}_sr.pi'.format(event_name), overwrite=True)

#bg_header
primary_hdu = fits.PrimaryHDU()
bg_spectrum.header.append(('HDUCLASS','OGIP','format conforms to OGIP standard'))
bg_spectrum.header.append(('HDUVERS1','1.2.0   ','Obsolete - included for backwards compatibility'))
bg_spectrum.header.append(('HDUVERS','1.2.0   ','Version of format (OGIP memo OGIP-92-007)'))
bg_spectrum.header.append(('HDUCLAS2','DERIVED ','WARNING This is NOT an OGIP-approved value'))
bg_spectrum.header.append(('HDUCLAS3','COUNT   ','PHA data stored as Counts (not count/s)'))
bg_spectrum.header.append(('TLMIN1',0,'Lowest legal channel number'))
bg_spectrum.header.append(('TLMAX1',2047,'Highest legal channel number'))
bg_spectrum.header.append(('TELESCOP','GROWTH','mission name'))
bg_spectrum.header.append(('INSTRUME',header['DET_ID'],'detector ID'))
bg_spectrum.header.append(('FILTER','NONE    ','filter in use'))
bg_spectrum.header.append(('EXPOSURE',1800.0,'exposure (in seconds)'))
bg_spectrum.header.append(('AREASCAL',1.000000E+00,'area scaling factor'))
bg_spectrum.header.append(('BACKFILE','NONE    ','associated background filename'))
bg_spectrum.header.append(('BACKSCAL',1.000000E+00,'background file scaling factor'))
bg_spectrum.header.append(('CORRFILE','NONE    ','associated correction filename'))
bg_spectrum.header.append(('CORRSCAL',1.000000E+00,'correction file scaling factor'))
bg_spectrum.header.append(('RESPFILE','NONE    ','associated redistrib matrix filename'))
bg_spectrum.header.append(('ANCRFILE','NONE    ','associated ancillary response filename'))
bg_spectrum.header.append(('PHAVERSN','1992a   ','obsolete'))
bg_spectrum.header.append(('DETCHANS',2048,'total number possible channels'))
bg_spectrum.header.append(('CHANTYPE','PI      ','channel type (PHA, PI etc)'))
bg_spectrum.header.append(('POISSERR',True,'Poissonian errors are applicable'))
bg_spectrum.header.append(('SYS_ERR',0,'no systematic error specified'))
bg_spectrum.header.append(('GROUPING',0,'no grouping of the data has been defined'))
bg_spectrum.header.append(('EVENTDAT',datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S').strftime('%Y%m%d'),'event date (JST)'))
bg_spectrum.header.append(('EVENTNAM',event_name,'event name'))

#bg_output
bg_hdul = fits.HDUList([primary_hdu, bg_spectrum])
bg_hdul.writeto('{}_bg.pi'.format(event_name), overwrite=True)