#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
from array import array

#definition
def near(series, value):
    if abs(series[series.searchsorted(value)] - value) > abs(series[series.searchsorted(value)-1] - value):
        return series[series.searchsorted(value)-1]
    else:
        return series[series.searchsorted(value)]

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python lightcurve_jst_rain.py <fitsfile> <adcchannel> <binwidth (sec)> <energylimitslow (MeV)> <energylimitshigh (MeV)> <xrain> <ido_kenshutsuki> <keido_kenshutsuki>')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimits_low=float(argv[4]) * 1000
energylimits_high=float(argv[5]) * 1000
xrain = argv[6]
ido_kenshutsuki = float(argv[7])
keido_kenshutsuki = float(argv[8])

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high)].reset_index(drop=True)
header = evt[1]

xrain_data = pd.read_csv(xrain)
ido_series = xrain_data.ido.unique()
keido_series = xrain_data.keido.unique()
ido_kenshutsuki_near = near(ido_series, ido_kenshutsuki)
keido_kenshutsuki_near = near(keido_series, keido_kenshutsuki)
rainfall = xrain_data[(xrain_data.ido == ido_kenshutsuki_near) & (xrain_data.keido == keido_kenshutsuki_near)].sort_values('time').reset_index()

#parameter
event_number = len(data.index)
observation_time = data.unixTime[-1:] - data.unixTime[0]
bin_number = math.floor(observation_time / binwidth)
bin_start = data.unixTime[0]
bin_end = data.unixTime[0] + binwidth * bin_number
n = len(rainfall.index)
x, y = array('d'), array('d')
for i in range(n):
    x.append(rainfall.time[i])
    y.append(rainfall.rain[i])

#hist
hist = ROOT.TH1F("hist","lightcurve",bin_number,bin_start,bin_end)

for i in range(event_number):
    hist.Fill(data.unixTime[i])
    
#graph
gr = ROOT.TGraph(n, x, y)

#canvas
c0=ROOT.TCanvas("c0", "canvas0", 640, 480)
scaleFactor=1.0/binwidth
hist.Sumw2()
hist.Scale(scaleFactor)
hist.SetTitle("Count Rate")
hist.GetXaxis().SetTitle("Time (JST)")
hist.GetXaxis().SetTitleOffset(1.2)
hist.GetXaxis().CenterTitle
hist.GetXaxis().SetRangeUser(bin_start, bin_end)
hist.GetYaxis().SetTitle("Count Rate (count/sec)")
hist.GetYaxis().CenterTitle
hist.GetYaxis().SetTitleOffset(1.35)
hist.SetStats(0)
hist.GetXaxis().SetLabelSize(0.045)
hist.GetYaxis().SetLabelSize(0.045)
ROOT.gStyle.SetTimeOffset(-788918400)
ROOT.gStyle.SetNdivisions(350)
hist.GetXaxis().SetTimeDisplay(1)
#hist.GetXaxis().SetTimeFormat("%m/%d %H:%M")
hist.GetXaxis().SetTimeFormat("%H:%M")
ROOT.TGaxis(1, 1, 1, 10, 0.0, 5.0, ndiv = 0.1, chopt = "+L", gridlength = 0)
gr.GetYaxis().SetTitle("Precipitation (mm/h)")

hist.Draw()
hist.Draw("e1")
gr.Draw("l")
c0.Update

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]
         