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
    print('Usage: python pi_making_after.py <fitsfile> <post_fitsfile> <adcchannel> <start_time> <end_time>(%Y-%m-%d %H:%M:%S.%f) <event_name>')
    quit()
    
#input
filename = argv[1]
post_filename = argv[2]
adcchannel = int(argv[3])
start_time = datetime.strptime(argv[4], '%Y-%m-%d %H:%M:%S.%f').timestamp()
end_time = datetime.strptime(argv[5], '%Y-%m-%d %H:%M:%S.%f').timestamp()
event_name = argv[6]

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[data.boardIndexAndChannel.astype('int') == adcchannel].reset_index(drop=True)
header = evt[1]
energy_width = header['BINW_CH{}'.format(adcchannel)]
data['true_energy'] = data.energy + energy_width*np.random.uniform(-0.5, 0.5, size=data.energy.shape)

post_evt = fits.getdata(post_filename, 1, header=True)
post_data = pd.DataFrame(np.array(post_evt[0]).byteswap().newbyteorder())
post_data = post_data[post_data.boardIndexAndChannel.astype('int') == adcchannel].reset_index(drop=True)
post_header = post_evt[1]
post_energy_width = post_header['BINW_CH{}'.format(adcchannel)]
post_data['true_energy'] = post_data.energy + post_energy_width*np.random.uniform(-0.5, 0.5, size=post_data.energy.shape)

merged_data = pd.concat([post_data, data], ignore_index=True)
bg_data = merged_data[(((merged_data.unixTime > start_time-300.0) & (merged_data.unixTime < start_time)) | ((merged_data.unixTime > end_time) & (merged_data.unixTime < end_time+300.0)))].reset_index(drop=True)
event_data = merged_data[(merged_data.unixTime > start_time) & (merged_data.unixTime < end_time)].reset_index(drop=True)
print('sr_photon_number = {}'.format(len(event_data.index)))
print('bg_photon_number = {}'.format(len(bg_data.index)))
    
#pi
bin_number = 2048
hist = np.histogram(event_data.true_energy, bins=bin_number, range=(40, 41000))
channel = fits.Column(name='CHANNEL', array=np.arange(2048), format='J')
counts = fits.Column(name='COUNTS', array=hist[0], format='J')
spectrum = fits.BinTableHDU.from_columns([channel, counts])
spectrum.name = 'SPECTRUM'

bg_hist = np.histogram(bg_data.true_energy, bins=bin_number, range=(40, 41000))
bg_counts = fits.Column(name='COUNTS', array=bg_hist[0], format='J')
bg_spectrum = fits.BinTableHDU.from_columns([channel, bg_counts])
bg_spectrum.name = 'SPECTRUM'

#sr_header
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
spectrum.header.append(('EVENTDAT',datetime.strptime(argv[4], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y%m%d'),'event date (JST)'))
spectrum.header.append(('EVENTNAM',event_name,'event name'))

#sr_output
hdul = fits.HDUList([primary_hdu, spectrum])
hdul.writeto('{}_sr.pi'.format(event_name), overwrite=True)

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
bg_spectrum.header.append(('EXPOSURE',600.0,'exposure (in seconds)'))
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
bg_spectrum.header.append(('EVENTDAT',datetime.strptime(argv[5], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y%m%d'),'event date (JST)'))
bg_spectrum.header.append(('EVENTNAM',event_name,'event name'))

#bg_output
bg_hdul = fits.HDUList([primary_hdu, bg_spectrum])
bg_hdul.writeto('{}_bg.pi'.format(event_name), overwrite=True)