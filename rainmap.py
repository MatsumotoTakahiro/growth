#! /usr/local/var/pyenv/shims/python

import os
import sys
import math
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_toolkits.basemap import Basemap

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python rainmap.py <dataset> <event_time> <ido_kenshutsuki> <keido_kenshutsuki> <resolution> <output_filename>')
    quit()

dataset = argv[1]
event_time = argv[2]
ido_kenshutsuki = float(argv[3])
keido_kenshutsuki = float(argv[4])
reso = argv[5]
output_filename = argv[6]

#input
data = pd.read_csv(dataset)
event_time_min = event_time[:-10]
event_time_stamp = datetime.strptime(event_time_min, '%Y-%m-%d %H:%M').timestamp()
event_data = data[(data.time > event_time_stamp-5.0) & (data.time < event_time_stamp+5.0)].reset_index(drop=True)
event_data = event_data.sort_values(['ido', 'keido']).reset_index(drop=True)

#parameter
latitude = np.sort(event_data.ido.unique())
longitude = np.sort(event_data.keido.unique())
ido_width = latitude[2] - latitude[1]
keido_width = longitude[2] - longitude[1]

#map
geo = Basemap(projection='merc', resolution='{}'.format(reso), llcrnrlon=longitude[0]-keido_width*0.5,  llcrnrlat=latitude[0]-ido_width*0.5, urcrnrlon=longitude[-1]+keido_width*0.5, urcrnrlat=latitude[-1]+ido_width*0.5)
geo.drawmapboundary()
geo.drawcoastlines()

#contour
X, Y = np.meshgrid(longitude, latitude)
print(len(longitude))
print(len(latitude))
print(len(event_data.rain))
Z = event_data.rain.values.reshape(len(latitude), len(longitude))
geo.pcolor(X, Y, Z, cmap="GnBu")
geo.colorbar(ticks=[0.1,0.5,1.0])

#observer_point
geo.plot(keido_kenshutsuki, ido_kenshutsuki, 'o', latlon=True)
plt.savefig(output_filename)
plt.show()