#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
from ROOT import TCanvas, gStyle, TH1D
import sys

#input
argv = sys.argv
filename = argv[1]
adcchannel=int(argv[2])
binwidth=float(argv[3])
energylimitslow=int(argv[4])
energylimitshigh=int(argv[5])

#read
evt = fits.open(filename)
data = pd.DataFrame(evt[1].data)
timetag = data.timeTag[(adcchannel==data.boardIndexAndChannel) & (data.phaMax>=energylimitslow) & (data.phaMax<energylimitshigh)].reset_index(drop=True)

#time
eventtime = np.zeros(len(timetag))
eventtime[0] = timetag[0]

for i in range(1,len(timetag)):
    eventtime[i] = timetag[i]
    if eventtime[i] == 0:
        eventtime[i] = eventtime[i-1]
    elif eventtime[i] < eventtime[i-1] :
        eventtime[i] += 2**40
    else:
        pass

eventtime = eventtime / 1e8
starttimetag = eventtime[0]
endtimetag = eventtime[len(timetag) -1]

observationtime = (endtimetag-starttimetag)
binstart = starttimetag
binend = endtimetag

print(binstart, binend)

#hist
binnum = int(observationtime/binwidth)

hist = TH1D("","",binnum,binstart,binend)

print(binnum)

for i in range(len(timetag)):
    hist.Fill(eventtime[i])

#canvas
c0=TCanvas("c0", "canvas0", 640, 480)
scaleFactor=1.0/binwidth
hist.Sumw2()
hist.Scale(scaleFactor)
hist.SetTitle("Count Rate")
hist.GetXaxis().SetTitle("second(sec)")
hist.GetXaxis().SetTitleOffset(1.2)
hist.GetXaxis().CenterTitle
hist.GetXaxis().SetRangeUser(binstart, binend)
hist.GetYaxis().SetTitle("Count Rate (count/sec)")
hist.GetYaxis().CenterTitle
hist.GetYaxis().SetTitleOffset(1.35)
hist.SetStats(0)
# gStyle.SetTimeOffset(-788918400)
# gStyle.SetNdivisions(505)
# hist.GetXaxis().SetTimeDisplay(1)
#hist.GetXaxis().SetTimeFormat("%m/%d %H:%M")
# hist.GetXaxis().SetTimeFormat("%H:%M:%S")

hist.Draw("e1")
c0.Update

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = raw_input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]