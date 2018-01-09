#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import sys
import subprocess
import re
import datetime
import markdown
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn

detector_list = ['growth-fy2016a', 'growth-fy2016b']

class DetectorNotExist(Exception):
    def __str__(self): 
        return "This detector is not exist."
    
class DetectorNotReact(Exception):
    def __str__(self):
        return "This detector do not react to 'ping'."
        
class DetectorDaqError(Exception):
    def __str__(self):
        return "This detector's daq is not ok."
        
class DetectorHkError(Exception):
    def __str__(self):
        return "This detector's hk is not ok."
        
class DetectorHvError(Exception):
    def __str__(self):
        return "This detector's high.vol. is not ok."

class Detector():    
    def __init__(self, id):
        if id in detector_list:
            super().__init__()
            self.detector_id = id
        else:
            raise DetectorNotExist()
    def is_active(self):
        returncode = subprocess.run('rsync {}:/home/pi/growth_config.yaml'.format(self.detector_id)\
                                    , stdout=subprocess.PIPE, shell=True).returncode
        if returncode == 0:
            return True
        else:
            raise DetectorNotReact()
    def hk_data(self, date):
        today = date
        yesterday = (datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(days=-1)).strftime('%Y%m%d')
        tomorrow = (datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d')
        if self.is_active() == True:
            rsync_out_today = subprocess.run('rsync -v {}:/home/pi/work/growth/data/{}/hk_{}* .'.format(self.detector_id, self.detector_id, date)\
                                             , stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            rsync_out_yesterday = subprocess.run('rsync -v {}:/home/pi/work/growth/data/{}/hk_{}* .'.format(self.detector_id, self.detector_id, yesterday)\
                                                    , stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            key_today = re.compile('hk_{}_\d+\.\w+'.format(date))
            key_yesterday = re.compile('hk_{}_\d+\.\w+'.format(yesterday))
            filename_today = key_today.search(rsync_out_today).group(0)
            filename_yesterday = key_yesterday.search(rsync_out_yesterday).group(0)
            if filename_today.find('gz'):
                subprocess.run('gzip -d {}'.format(filename_today)\
                               , stdout=subprocess.PIPE, shell=True)
                filename_today = filename_today.rstrip('.gz')
            hk_today = pd.read_json(filename_today, orient='records', lines=True)
            if filename_yesterday.find('gz'):
                subprocess.run('gzip -d {}'.format(filename_yesterday)\
                               , stdout=subprocess.PIPE, shell=True)
                filename_yesterday = filename_yesterday.rstrip('.gz')
            hk_yesterday = pd.read_json(filename_yesterday, orient='records', lines=True)
            
            if today == datetime.date.today().strftime('%Y%m%d'):
                print('hk has not prepared')
                quit()
            elif today == (datetime.date.today() + datetime.timedelta(days=-1)).strftime('%Y%m%d'):
                hk_data = pd.concat([hk_yesterday, hk_today], ignore_index=True)\
                    [(pd.to_datetime(today)<pd.concat([hk_yesterday,hk_today], ignore_index=True)['timestamp'])\
                    &(pd.concat([hk_yesterday,hk_today], ignore_index=True)['timestamp']<pd.to_datetime(datetime.datetime.today()))]
            else:
                rsync_out_tomorrow = subprocess.run('rsync -v {}:/home/pi/work/growth/data/{}/hk_{}* .'.format(self.detector_id, self.detector_id, tomorrow)\
                                             , stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
                key_tomorrow = re.compile('hk_{}_\d+\.\w+'.format(tomorrow))
                filename_tomorrow = key_tomorrow.search(rsync_out_tomorrow).group(0)
                if filename_today.find('gz'):
                    subprocess.run('gzip -d {}'.format(filename_tomorrow)\
                               , stdout=subprocess.PIPE, shell=True)
                    filename_tomorrow = filename_tomorrow.rstrip('.gz')
                hk_tomorrow = pd.read_json(filename_tomorrow, orient='records', lines=True)
                hk_data = pd.concat([hk_yesterday,hk_today,hk_tomorrow], ignore_index=True)\
                    [(pd.to_datetime(today)<pd.concat([hk_yesterday,hk_today,hk_tomorrow], ignore_index=True)['timestamp'])\
                    &(pd.concat([hk_yesterday,hk_today,hk_tomorrow], ignore_index=True)['timestamp']<pd.to_datetime(tomorrow))]
                            
            hk_output = pd.DataFrame({'temperature':[], 'hv0':[], 'hv1':[], 'time':[], 'humidity':[], 'pressure':[]})
            
            for i in range(len(hk_data.timestamp)):
                if hk_data.iloc[i].daq['status'] != 'ok':
                    raise DetectorDaqError()
                else:
                    if hk_data.iloc[i].hk['status'] != 'ok':
                        raise DetectorHkError()
                    else: 
                        if hk_data.iloc[i].hv['status'] != 'ok':
                            raise DetectorHvError()
                        else:
                            hk_piece = pd.DataFrame({'temperature':[hk_data.iloc[i].hk['hk']['bme280']['temperature']['value']]\
                                                    ,'hv1':[hk_data.iloc[i].hv['0']['value_in_mV']]\
                                                    ,'hv2':[hk_data.iloc[i].hv['1']['value_in_mV']]\
                                                    , 'time':[hk_data.iloc[i].timestamp]\
                                                    , 'humidity':[hk_data.iloc[i].hk['hk']['bme280']['humidity']['value']]\
                                                    , 'pressure':[hk_data.iloc[i].hk['hk']['bme280']['pressure']['value']]})
                            hk_output = hk_output.append(hk_piece)
                            hk_output = hk_output.reset_index(drop=True)
                            
            subprocess.run('rm *.text', stdout=subprocess.PIPE, shell=True)
            
            return hk_output

            
def get_hk_data(detector_list, date):
    data_list = pd.DataFrame({'detectorID':[],'data':[], 'status':[]})    
    for i in detector_list:
        try:
            data_list = data_list.append(pd.DataFrame({'detectorID':[i], 'data':[Detector(i).hk_data(date)], 'status':'ok'}))
        except DetectorNotReact:
            data_list = data_list.append(pd.DataFrame({'detectorID':[i], 'data':[np.nan], 'status':'no reaction'}))
        except DetectorDaqError:
            data_list = data_list.append(pd.DataFrame({'detectorID':[i], 'data':[np.nan], 'status':'daq error'}))
        except DetectorHkError:
            data_list = data_list.append(pd.DataFrame({'detectorID':[i], 'data':[np.nan], 'status':'hk error'}))
        except DetectorHvError:
            data_list = data_list.append(pd.DataFrame({'detectorID':[i], 'data':[np.nan], 'status':'high.vol. error'}))
        finally:
            data_list = data_list.reset_index(drop=True)
            
    return data_list
    
def plot_temperature(data_list,date):
    fig, ax = plt.subplots()
    for i in range(len(data_list.detectorID)):
        if data_list.iloc[i]['status'] == 'ok':
            plt.plot(data_list.iloc[i]['data'].time, data_list.iloc[i]['data'].temperature, label=data_list.iloc[i]['detectorID'])
    plt.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('time')
    plt.ylabel('temperature(degC)')
    plt.savefig('temperature_{}.png'.format(date))
    return 'temperature_{}.png'.format(date)
    
def plot_humidity(data_list,date):
    fig, ax = plt.subplots()
    for i in range(len(data_list.detectorID)):
        if data_list.iloc[i]['status'] == 'ok':
            plt.plot(data_list.iloc[i]['data'].time, data_list.iloc[i]['data'].humidity, label=data_list.iloc[i]['detectorID'])
    plt.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('time')
    plt.ylabel('humidity(%)')
    plt.savefig('humidity_{}.png'.format(date))
    return 'humidity_{}.png'.format(date)

def plot_pressure(data_list,date):
    fig, ax = plt.subplots()
    for i in range(len(data_list.detectorID)):
        if data_list.iloc[i]['status'] == 'ok':
            plt.plot(data_list.iloc[i]['data'].time, data_list.iloc[i]['data'].pressure, label=data_list.iloc[i]['detectorID'])
    plt.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('time')
    plt.ylabel('pressure(mb)')
    plt.savefig('pressure_{}.png'.format(date))
    return 'pressure_{}.png'.format(date)
    
def plot_highvol1(data_list,date):
    fig, ax = plt.subplots()
    for i in range(len(data_list.detectorID)):
        if data_list.iloc[i]['status'] == 'ok':
            plt.plot(data_list.iloc[i]['data'].time, data_list.iloc[i]['data'].hv1, label=data_list.iloc[i]['detectorID'])
    plt.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('time')
    plt.ylabel('High Voltage 1(mV)')
    plt.savefig('highvol1_{}.png'.format(date))
    return 'highvol1_{}.png'.format(date)   
    
def plot_highvol2(data_list,date):
    fig, ax = plt.subplots()
    for i in range(len(data_list.detectorID)):
        if data_list.iloc[i]['status'] == 'ok':
            plt.plot(data_list.iloc[i]['data'].time, data_list.iloc[i]['data'].hv2, label=data_list.iloc[i]['detectorID'])
    plt.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xlabel('time')
    plt.ylabel('High Voltage 2(mV)')
    plt.savefig('highvol2_{}.png'.format(date))
    return 'highvol2_{}.png'.format(date)   
            
if __name__ == '__main__':
    #argv
    argv = sys.argv
    if len(argv) < 2:
        print('When?')
        quit()
    elif len(argv) == 2:
        date = argv[1]
    else:
        print('Too many argument!')
        quit()
        
    data_list = get_hk_data(detector_list, date)
    
    temperature_name = plot_temperature(data_list, date)
    humidity_name = plot_humidity(data_list, date)
    pressure_name = plot_pressure(data_list, date)
    highvol1_name = plot_highvol1(data_list, date)
    highvol2_name = plot_highvol2(data_list, date)
    
    report_markdown = '''
#**Operation Report {}**

##Detector status
{}
  
##Temperature
<img src="{}" width=50%>

##Humidity
<img src="{}" width=50%>

##Pressure
<img src="{}" width=50%>

##High Voltage 1
<img src="{}" width=50%>

##High Voltage 2
<img src="{}" width=50%>
'''.format(date, '* {} : {}\n{}', temperature_name, humidity_name, pressure_name, highvol1_name, highvol2_name)
            
    for i in range(len(data_list.detectorID)):
        report_markdown = report_markdown.format(data_list.iloc[i].detectorID, data_list.iloc[i].status, '* {} : {}\n{}')
        
    report_html = markdown.Markdown().convert(report_markdown)
    
    output_markdown = open('observation_report_{}.md'.format(date), 'w')
    output_html = open('observation_report_{}.html'.format(date), 'w')
    
    output_markdown.write(report_markdown)
    output_html.write(report_html)
    
    output_markdown.close()
    output_html.close()
