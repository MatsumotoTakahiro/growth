#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import sys
import subprocess
import re
import datetime

detector_list = ['growth-fy2016a','growth-fy2016b']

class DetectorNotExist(Exception):
    def __str__(self): 
        return "This detector is not exist."
    
class DetectorNotReaction(Exception):
    def __str__(self):
        return "This detector do not react to 'ping'"

class Detector(pd.DataFrame):    
    def __init__(self, id):
        if id in detector_list:
            super().__init__()
            self.detector_id = id
        else:
            raise DetectorNotExist()
    def is_active(self):
        returncode = subprocess.run('rsync {}:/home/pi/growth_config.yaml'.format(detector_id)\
                                    , stdout=subprocess.PIPE, shell=True).returncode
        if returncode == 0:
            return True
        else:
            raise DetectorNotReaction()
    def hk_data(self, date=datetime.date.today().strftime('%Y%m%d')):
        yesterday = str(int(date)-1)
        if self.is_active == True:
            rsync_out_today = subprocess.run('rsync -v {}:/home/pi/work/growth/data/{}/hk_{}*'.format(self.detector_id, self.detector_id, date)\
                                             , stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            rsync_out_yesterdayday = subprocess.run('rsync -v {}:/home/pi/work/growth/data/{}/hk_{}* .'.format(self.detector_id, self.detector_id, yesterday)\
                                                    , stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            key_today = re.compile('hk_{}_\d+\.\w+'.format(date))
            key_yesterday = re.compile('hk_{}_\d+\.\w+'.format(yesterday))
            filename_today = key_today.search(rsync_out_today).group(0)
            filename_yesterday = key_yesterday.search(rsync_out_yesterday).group(0)
            if filename_today.find('gz'):
                subprocess.run('gzip -d {}'.format(filename_today)\
                               , stdout=subprocess.PIPE, shell=True)
                filename_today = 
            if filename_yesterday.find('gz'):
                subprocess.run('gzip -d {}'.format(filename_yesterday)\
                               , stdout=subprocess.PIPE, shell=True)
                
            return pd.read_csv(filename)
        
def a