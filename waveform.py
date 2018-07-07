#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys
import math
from datetime import datetime
from array import array
import matplotlib.pyplot as plt

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python waveform_wave.py <fitsfile> <adcchannel> <start_time>(%Y/%m/%d %H:%M:%S:%f(5-digit)) <duration(sec)>')
    quit()

filename = argv[1]
adcchannel=int(argv[2])
start_time = datetime.strptime(argv[3], '%Y/%m/%d %H:%M:%S:%f').timestamp()
duration = float(argv[4])

#read
evt = fits.getdata(filename, 1, header=True)
data = pd.DataFrame(np.array(evt[0]).byteswap().newbyteorder())
data = data[(data.boardIndexAndChannel.astype('int') == adcchannel) & (data.unixTime > start_time-0.02) & (data.unixTime < start_time+duration)].reset_index(drop=True)
header = evt[1]
data.to_csv('nae.csv')

#array
unix_time, pha_max, pha_min = array( 'd' ), array( 'd' ), array('d')
for i in range(len(data.index)):
    unix_time.append(data.unixTime[i]-start_time)
    pha_max.append(data.phaMax[i]+2**15)
    pha_min.append(data.phaMin[i]+2**15)

#canvas
c0=ROOT.TCanvas("c0", "canvas0", 640, 480)
frame = c0.DrawFrame(-0.03, 0, 0.3, 4000)
phamax = ROOT.TGraph(len(data.index), unix_time, pha_max)
phamin = ROOT.TGraph(len(data.index), unix_time, pha_min)
phamax.SetMarkerStyle(8)
phamax.SetMarkerColor(2)
phamax.SetMarkerSize(0.3)
phamin.SetMarkerStyle(8)
phamin.SetMarkerColor(1)
phamin.SetMarkerSize(0.3)

phamax.SetTitle("Count Rate")
phamax.GetXaxis().SetTitle("Second from {}".format(argv[3]))
phamax.GetXaxis().SetTitleOffset(1.2)
phamax.GetXaxis().CenterTitle

phamax.GetYaxis().SetTitle("ADC channel value")
phamax.GetYaxis().CenterTitle
phamax.GetYaxis().SetTitleOffset(1.55)

phamax.GetXaxis().SetLabelSize(0.045)
phamax.GetYaxis().SetLabelSize(0.045)

ROOT.gStyle.SetTimeOffset(-788918400)
ROOT.gStyle.SetNdivisions(505)
#phamax.GetXaxis().SetTimeDisplay(1)
#phamin.GetXaxis().SetTimeDisplay(1)
#hist.GetXaxis().SetTimeFormat("%m/%d %H:%M")
#hist.GetXaxis().SetTimeFormat("%H:%M")

c0.Update()
phamax.Draw("AP")
phamin.Draw("P")
c0.Update()

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]