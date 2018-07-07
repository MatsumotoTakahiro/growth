#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
import random
from datetime import datetime

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python lightcurve_jst_modified_forshort.py <fitsfile> <adcchannel> <binwidth (sec)> <energylimitslow (MeV)> <energylimitshigh (MeV)> <start_time>(%Y/%m/%d %H:%M:%S:%f(5-digit)) <duration(sec)>')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimits_low=float(argv[4]) * 1000
energylimits_high=float(argv[5]) * 1000
start_time = datetime.strptime(argv[6], '%Y/%m/%d %H:%M:%S:%f').timestamp()
duration = float(argv[7])

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.energy > energylimits_low) & (data.energy < energylimits_high) & (data.unixTime > start_time-0.1) & (data.unixTime < start_time+duration)].reset_index(drop=True)
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
hist = ROOT.TH1F("hist","lightcurve",bin_number,bin_start-start_time,bin_end-start_time)
hist_dead = ROOT.TH1F("hist_dead","lightcurve",bin_number,bin_start-start_time,bin_end-start_time)
hist_corrected = ROOT.TH1F("hist_corrected","lightcurve",bin_number,bin_start-start_time,bin_end-start_time)

for i in range(event_number):
    hist.Fill(data.unixTime[i]-start_time)
    
for i in range(len(trigger_data.index)-1):
    if trigger_data.delta_trigger[i]>1:
        for j in range(trigger_data.delta_trigger[i]-1):
            hist_dead.Fill(random.uniform(trigger_data.unix_time[i], trigger_data.unix_time[i+1])-start_time)
            
for i in range(event_number):
    if (data.energy[i] > energylimits_low) & (data.energy[i] < energylimits_high):
        hist_corrected.Fill(data.unixTime[i]-start_time)
        
hist.Sumw2()
#hist_corrected.Scale(1.0 / binwidth)
#for i in range(1, bin_number):
#    scale_factor = (hist[i] + hist_dead[i]) / hist[i]
#    hist_corrected[i] = hist_corrected[i]*scale_factor
#    hist_corrected.SetBinError(i, hist_corrected.GetBinError(i)*scale_factor)

#canvas
c0=ROOT.TCanvas("c0", "canvas0", 640, 480)
hist_corrected.SetTitle("Count Rate")
hist_corrected.GetXaxis().SetTitle("Second from {}".format(argv[6]))
hist_corrected.GetXaxis().SetTitleOffset(1.2)
hist_corrected.GetXaxis().CenterTitle
hist_corrected.GetXaxis().SetRangeUser(bin_start, bin_end)
hist_corrected.GetYaxis().SetTitle("Count Rate (count/bin)")
hist_corrected.GetYaxis().CenterTitle
hist_corrected.GetYaxis().SetTitleOffset(1.35)
hist_corrected.SetStats(0)
hist_corrected.GetXaxis().SetLabelSize(0.045)
hist_corrected.GetYaxis().SetLabelSize(0.045)
ROOT.gStyle.SetTimeOffset(-788918400)
ROOT.gStyle.SetNdivisions(505)
#hist_corrected.GetXaxis().SetTimeDisplay(1)
#hist.GetXaxis().SetTimeFormat("%m/%d %H:%M")
#hist_corrected.GetXaxis().SetTimeFormat("%H:%M")

hist_corrected.Draw()
hist_corrected.Draw("e1")
c0.Update

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]