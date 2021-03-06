#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python lightcurve_jst.py <fitsfile> <adcchannel> <binwidth (sec)> <energylimitslow (MeV)> <energylimitshigh (MeV)>')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimits_low=float(argv[4]) * 1000
energylimits_high=float(argv[5]) * 1000
filename2 = argv[6]

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high)].reset_index(drop=True)
header = evt[1]

evt2 = fits.getdata(filename2, 1, header=True)
data2 = pd.DataFrame(np.array(evt2[0]).byteswap().newbyteorder())
data2 = data2[(data2.boardIndexAndChannel.astype('int') == adcchannel) & (data2.energy > energylimits_low) & (data2.energy < energylimits_high)].reset_index(drop=True)

#parameter
event_number = len(data.index) + len(data2.index)
event_number1 = len(data.index) 
event_number2 = len(data2.index)
observation_time = data2.unixTime[-1:] - data.unixTime[0]
bin_number = math.floor(observation_time / binwidth)
bin_start = data.unixTime[0]
bin_end = data.unixTime[0] + binwidth * bin_number

#hist
hist = ROOT.TH1F("hist","lightcurve",bin_number,bin_start,bin_end)

for i in range(event_number1):
    hist.Fill(data.unixTime[i])
    
for i in range(event_number2):
    hist.Fill(data2.unixTime[i])

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
ROOT.gStyle.SetTimeOffset(-788918400)
ROOT.gStyle.SetNdivisions(505)
hist.GetXaxis().SetTimeDisplay(1)
#hist.GetXaxis().SetTimeFormat("%m/%d %H:%M")
hist.GetXaxis().SetTimeFormat("%H:%M")

hist.Draw()
hist.Draw("e1")
c0.Update

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]