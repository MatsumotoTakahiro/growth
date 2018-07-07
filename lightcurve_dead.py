#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
import random

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python lightcurve_dead.py <fitsfile> <adcchannel> <binwidth (sec)> ')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[data.boardIndexAndChannel.astype('int') == adcchannel].reset_index(drop=True)
header = evt[1]

trigger_data = pd.DataFrame({
    'delta_trigger':np.roll(data.triggerCount, -1) - data.triggerCount,
    'unix_time':data.unixTime
})

#parameter
event_number = len(data.index)
observation_time = data.unixTime[-1:] - data.unixTime[0]
bin_number = math.floor(observation_time / binwidth)
bin_start = data.unixTime[0]
bin_end = data.unixTime[0] + binwidth * bin_number

#hist
hist = ROOT.TH1F("hist","lightcurve",bin_number,bin_start,bin_end)
    
for i in range(len(trigger_data.index)-1):
    if trigger_data.delta_trigger[i]>1:
        for j in range(trigger_data.delta_trigger[i]-1):
            hist.Fill(random.uniform(trigger_data.unix_time[i], trigger_data.unix_time[i+1]))

scalefactor = 1.0 / binwidth

#canvas
c0=ROOT.TCanvas("c0", "canvas0", 640, 480)
hist.Sumw2()
hist.Scale(scalefactor)
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