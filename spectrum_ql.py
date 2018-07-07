#! /usr/local/var/pyenv/shims/python

import numpy as np
import pandas as pd
from astropy.io import fits
import ROOT
import sys

#input
argv = sys.argv
filename = argv[1]
adcchannel = int(argv[2])
rebin = int(argv[3])

#read
evt = fits.open(filename)
data = pd.DataFrame(evt[1].data)

#time
starttimetag = data.timeTag[0]
endtimetag = data.timeTag[len(data.index) -1]

if starttimetag > endtimetag :
    observationtime = float((endtimetag-starttimetag+2**40)/1e8)
else:
    observationtime = float((endtimetag - starttimetag)/1e8)

#hist
binnum = int(4096/rebin)
print(binnum, type(binnum))

hist = ROOT.TH1F("hist","spectrum",binnum,-0.5,4095.5)

for i in range(len(data.index)):
    if int(data.boardIndexAndChannel[i]) == adcchannel:
        hist.Fill(int(data.phaMax[i]))

scalefactor = 1.0/(observationtime*float(rebin))

#canvas
c = ROOT.TCanvas("myCanvasName","The Canvas Title;Channel;Count/s/ch",640,480)

hist.SetTitle("")
hist.GetXaxis().SetTitle("Channel")
hist.GetXaxis().SetTitleOffset(1.2)
hist.GetXaxis().CenterTitle()
hist.GetYaxis().SetTitle("Count/s/ch")
hist.GetYaxis().CenterTitle()
hist.GetYaxis().SetTitleOffset(1.35)
hist.GetYaxis().SetRangeUser(0.5, 100000)
hist.GetXaxis().SetRangeUser(2048, 4096)
hist.SetStats(0)
hist.Sumw2()
hist.Scale(scalefactor)
hist.Draw("e1")
c.SetLogy()
c.Update

#c.SaveAs("hoge.root")

#c.SaveAs("{}sp.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'Enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]