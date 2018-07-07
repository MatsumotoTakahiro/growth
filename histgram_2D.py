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
  print("Usage: python histgram_2D.py <input file> <adcchannel> <time bin width> <start_time> <end_time>(%Y/%m/%d %H:%M:%S:%f(5-digit))")
  quit()

energy_max=24.0
energy_min=0.4
energy_bin_number=40

argv = sys.argv
filename = argv[1]
adcchannel = int(argv[2])
time_binwidth = float(argv[3])
#start_time = float(argv[4])
#end_time = float(argv[5])
start_time = datetime.strptime(argv[4], '%Y/%m/%d %H:%M:%S:%f').timestamp()
end_time = datetime.strptime(argv[5], '%Y/%m/%d %H:%M:%S:%f').timestamp()

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.unixTime > start_time) & (data.unixTime < end_time)].reset_index(drop=True)
header = evt[1]

#pamameter
event_number = len(data.index)
observation_time = end_time - start_time
energy_width = header['BINW_CH{}'.format(adcchannel)]
time_bin_number = math.floor(observation_time / time_binwidth)

time_bins=np.zeros(time_bin_number + 1)
for i in range(len(time_bins)):
    time_bins[i] = start_time + i*time_binwidth

energy_log_min = math.log10(energy_min)
energy_log_max = math.log10(energy_max)
energy_bin_width = (energy_log_max - energy_log_min) / energy_bin_number
energy_bins = np.zeros(energy_bin_number + 1)
for i in range(len(energy_bins)):
    energy_bins[i] = 10**(energy_log_min + i*energy_bin_width)
energy_bins[0] = energy_min
energy_bins[energy_bin_number] = energy_max

#hist
hist2D = ROOT.TH2D("", "", time_bin_number, time_bins, energy_bin_number, energy_bins)

for i in range(event_number):
    randomized_energy = (data.energy[i] + random.uniform(-0.5,0.5)*energy_width)/1000.0
    if (randomized_energy >= energy_min) & (randomized_energy < energy_max):
        hist2D.Fill(data.unixTime[i], randomized_energy)

#canvas
c = ROOT.TCanvas("c0","canvas0",640,480)

hist2D.SetTitle("")
hist2D.GetXaxis().SetTitle("Time (JST)")
hist2D.GetXaxis().SetTitleOffset(1.2)
hist2D.GetXaxis().CenterTitle()
hist2D.GetYaxis().SetTitle("Energy (MeV)")
hist2D.GetYaxis().CenterTitle()
hist2D.GetYaxis().SetTitleOffset(1.35)
hist2D.GetXaxis().SetTimeDisplay(1)
hist2D.GetXaxis().SetTimeFormat("%H:%M:%S")
hist2D.SetStats(0)
hist2D.Draw("colz")
c.SetLogy()
c.Update()

#c.SaveAs("hoge.root")

#c.SaveAs("{}sp.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'Enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]