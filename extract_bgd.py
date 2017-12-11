#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys

#input
argv = sys.argv
filename = argv[1]
background = argv[2]
adcchannel = int(argv[3])
rebin = int(argv[4])

#read
evt1 = fits.open(filename)
data1 = pd.DataFrame(evt1[1].data)
evt2 = fits.open(background)
data2 = pd.DataFrame(evt2[1].data)

#time
starttimetag = data1.timeTag[0]
endtimetag = data1.timeTag[len(data1.index) -1]

if starttimetag > endtimetag :
    observationtime = float((endtimetag-starttimetag+2**40)/1e8)
else:
    observationtime = float((endtimetag - starttimetag)/1e8)

#hist
binnum = 4096/rebin

hist1 = ROOT.TH1F("hist","spectrum",binnum,-0.5,4095.5)
hist2 = ROOT.TH1F("hist2","spectrum",binnum,-0.5,4095.5)

for i in range(len(data1.index)):
    if int(data1.boardIndexAndChannel[i]) == adcchannel:
        hist1.Fill(int(data1.phaMax[i]))
        
for i in range(len(data2.index)):
    if int(data2.boardIndexAndChannel[i]) == adcchannel:
        hist2.Fill(int(data2.phaMax[i]))

scalefactor = 1.0/(observationtime*float(rebin))

hist1.Add(hist2, -1)

#canvas
c = ROOT.TCanvas("myCanvasName","The Canvas Title;Channel;Count/s/ch",640,480)

hist1.SetTitle("")
hist1.GetXaxis().SetTitle("Channel")
hist1.GetXaxis().SetTitleOffset(1.2)
hist1.GetXaxis().CenterTitle()
hist1.GetYaxis().SetTitle("Count/s/ch")
hist1.GetYaxis().CenterTitle()
hist1.GetYaxis().SetTitleOffset(1.35)
hist1.GetYaxis().SetRangeUser(0.5, 100000)
hist1.GetXaxis().SetRangeUser(2048, 4096)
hist1.SetStats(0)
hist1.Sumw2()
hist1.Scale(scalefactor)
hist1.Draw("e1")
c.SetLogy()
c.Update

#c.SaveAs("{}sp.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = raw_input( 'Enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]