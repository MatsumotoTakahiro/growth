#! /usr/local/bin/python3

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
from datetime import datetime
import random
import math

#input
if len(sys.argv) < 2:
  print("Usage: python spectrum_energy.py <input file> <adcchannel> <start_time> <end_time>(%Y/%m/%d %H:%M:%S:%f(5-digit))")
  quit()

energy_min = 0.1
energy_max = 30.0
energy_bin_number = 200

argv = sys.argv
filename = argv[1]
adcchannel = int(argv[2])
#start_time = float(argv[3])
#end_time = float(argv[4])
start_time = datetime.strptime(argv[3], '%Y/%m/%d %H:%M:%S:%f').timestamp()
end_time = datetime.strptime(argv[4], '%Y/%m/%d %H:%M:%S:%f').timestamp()

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.unixTime > start_time) & (data.unixTime < end_time)].reset_index(drop=True)
header = evt[1]

#pamameter
event_number = len(data.index)
observation_time = end_time - start_time
energy_width = header['BINW_CH{}'.format(adcchannel)]

energy_log_min = math.log10(energy_min)
energy_log_max = math.log10(energy_max)
energy_bin_width = (energy_log_max - energy_log_min) / energy_bin_number
energy_bins = np.zeros(energy_bin_number + 1)
for i in range(len(energy_bins)):
    energy_bins[i] = 10**(energy_log_min + i*energy_bin_width)
energy_bins[0] = energy_min
energy_bins[energy_bin_number] = energy_max

#hist
hist = ROOT.TH1F("hist","spectrum", energy_bin_number, energy_bins)

for i in range(event_number):
    randomized_energy = (data.energy[i] + random.uniform(-0.5,0.5)*energy_width)/1000.0
    if randomized_energy > 0:
        hist.Fill(randomized_energy)
        
photon_number = 0
for i in range(len(hist)):
    photon_number += hist.FindBin(i)
    
print('Photon number = {}'.format(photon_number))

hist.Sumw2()
for i in range(1, len(energy_bins)):
    scale_factor = 1 / (observation_time * (energy_bins[i] - energy_bins[i-1]))
    hist[i] = hist[i]*scale_factor
    hist.SetBinError(i, hist.GetBinError(i)*scale_factor)
#scale_factor = bin_number / (observation_time*energy_max)
#hist.Scale(scale_factor)

#canvas
c = ROOT.TCanvas("c0","canvas0",640,480)

hist.SetTitle("")
hist.GetXaxis().SetTitle("Energy (MeV)")
hist.GetXaxis().SetTitleOffset(1.2)
hist.GetXaxis().CenterTitle()
hist.GetYaxis().SetTitle("Count/s/Mev")
hist.GetYaxis().CenterTitle()
hist.GetYaxis().SetTitleOffset(1.35)
hist.GetYaxis().SetRangeUser(0.00001, 1000)
hist.GetXaxis().SetRangeUser(0.1, 15)
hist.SetStats(0)
hist.Draw()
hist.Draw("e1")
c.SetLogy()
#c.SetLogx()
c.Update

hist.SaveAs("hoge.root")

#c.SaveAs("{}sp.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'Enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]