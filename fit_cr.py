#! /usr/local/var/pyenv/shims/python

import sys
import numpy as np
import pandas as pd
import ROOT
import math

#input
argv = sys.argv

if len(argv) < 2:
    print('Usage: python fit_cr.py <dataset_name> <cr_binwidth (count/sec)>')
    quit()

dataset_name = argv[1]
cr_binwidth=float(argv[2])

#dataset
data = pd.read_csv(dataset_name, names=('time', 'cr', 'err'), dtype={'time':'float64', 'cr':'float64', 'err':'float64'})

#parameter
lc_number = len(data.index)
maxcount = data.cr.max()
bin_start = 0.0
bin_end = maxcount+5.0
bin_number = math.floor((bin_end - bin_start)/cr_binwidth)
        
#hist
cr_hist = ROOT.TH1F("cr_hist", "significance", bin_number, bin_start, bin_end)
for i in range(lc_number):
    cr_hist.Fill(data.cr[i])
    
cr_hist.Sumw2()
    
#canvas
c0=ROOT.TCanvas("c0", "canvas0", 640, 480)
cr_hist.SetTitle("histogram of count/bin")
cr_hist.GetXaxis().SetTitle("Count/bin")
cr_hist.GetXaxis().SetTitleOffset(1.2)
cr_hist.GetXaxis().CenterTitle
cr_hist.GetXaxis().SetRangeUser(bin_start, bin_end)
cr_hist.GetYaxis().SetTitle("Bin Frequency")
cr_hist.GetYaxis().CenterTitle
cr_hist.GetYaxis().SetTitleOffset(1.35)
cr_hist.SetStats(0)
cr_hist.GetXaxis().SetLabelSize(0.045)
cr_hist.GetYaxis().SetLabelSize(0.045)
ROOT.gStyle.SetTimeOffset(-788918400)
ROOT.gStyle.SetNdivisions(505)

cr_hist.Draw()
c0.SetLogy()
c0.Update

#c0.SaveAs("{}lc.pdf".format(filename))

if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]

#botsu
#cr_hist = np.histogram(data.cr, bins=bin_number)
#
#fitting
#xdata = cr_hist[0]
#ydata = np.delete(cr_hist[1], -1) + 0.5*cr_binwidth
#parameter_initial = np.array([constant_initial, mean_initial, sigma_initial])
#
#def gaus(x, a, b, c):
#    return a*np.exp(-(x-b)**2 / (2*c**2))
#    
#fitting_param = scipy.optimize.curve_fit(gaus, xdata, ydata, p0=parameter_initial)
#print("Constant = {}\nMean = {}\nSigma = {}\n".format(fitting_param))
#result = gaus(xdata, fitting_param[0], fitting_param[1], fitting_param[2])
#
#eventsearch
#maxsigma = (cr_hist[0].max() - fitting_param[1]) / fitting_param[2]
#print("Max Sigma = {} at {}\n".format())
#
#figure
#plt.hist(data.cr, bins=math.floor((maxcount+5.0)/cr_binwidth))
#plt.plot(xdata, result, '-')
#plt.savefig('nae.pdf')