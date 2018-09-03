#! /usr/local/var/pyenv/shims/python

import os
import sys
import math
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python kisho_data.py <file_list> <ido_hokusei> <keido_hokusei> <ido_nantou> <keido_nantou> <ido_num> <keido_num> <output_filename>')
    quit()

file_list = argv[1]
ido_hokusei = float(argv[2])
keido_hokusei = float(argv[3])
ido_nantou = float(argv[4])
keido_nantou = float(argv[5])
ido_num = int(argv[6])
keido_num = int(argv[7])
output_filename = argv[8]

#input
name_list = pd.read_table(file_list, names=['data_name'])

#geo
ido_width = (ido_hokusei - ido_nantou) / ido_num
keido_width = (keido_nantou - keido_hokusei) / keido_num
geo_ido = np.empty(ido_num, dtype=np.float16)
geo_keido = np.empty(keido_num, dtype=np.float16)
geo_ido = np.arange(ido_nantou+0.5*ido_width, ido_hokusei+0.5*ido_width, step=ido_width)
geo_keido = np.arange(keido_hokusei+0.5*keido_width, keido_nantou+0.5*keido_width, step=keido_width)

#output
output = pd.DataFrame({'ido':[], 'keido':[], 'time':[], 'rain':[]})

for i in range(len(name_list.index)):
    data_csv = pd.read_csv(name_list['data_name'][i], header=None)
    time_file = datetime.strptime(name_list['data_name'][i].strip('.csv'), '%Y%m%d-%H%M').timestamp()
    for j in range(ido_num):
        for k in range(keido_num):
            if data_csv.iloc[j, k] == 0.1:
                true_rain = 0.0
            else:
                true_rain = data_csv.iloc[j, k]
            additional_line = pd.DataFrame({'ido':[geo_ido[ido_num-j-1]], 'keido':[geo_keido[k]], 'time':[time_file], 'rain':[true_rain]})
            output = output.append(additional_line, ignore_index=True)

output.to_csv(output_filename)
