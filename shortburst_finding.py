#! /usr/local/var/pyenv/shims/python

import sys
import numpy as np
import pandas as pd
from astropy.io import fits
#from tqdm import tqdm

def slidewindow(data, w, k, lag, t):
    rireki_matrix = np.zeros((w, k))
    test_matrix = np.zeros((w, k))
    
    for i in range(k):
        rireki_matrix[:,i] = data[t-k-w+1+i:t-k+1+i]
        test_matrix[:,i] = data[t+lag-k-w+1+i:t+lag-k+1+i]
        
    return rireki_matrix, test_matrix

def score(matrixA, matrixB, m):
    U, _, _ = np.linalg.svd(matrixA, full_matrices=False)
    Q, _, _ = np.linalg.svd(matrixB, full_matrices=False)
    
    Um = U[:, :m]
    Qm = Q[:, :m]
    
    UQ = np.dot(Um.T, Qm)
    _, sigma, _ = np.linalg.svd(UQ, full_matrices=False)
    score = 1 - sigma.max()*sigma.max()
    
    return score

if __name__ == '__main__':
    
    #argv
    argv = sys.argv
    fitsfile = argv[1]
    adcchannel=int(argv[2])
    bin_num = int(argv[3])
    energylimitslow=int(argv[4])
    energylimitshigh=int(argv[5])
    w = int(argv[6])
    k = int(argv[7])
    lag = int(argv[8])
    m = int(argv[9])
    
    #input
    evt = fits.open(fitsfile)
    data = pd.DataFrame(evt[1].data)
    timetag = data.timeTag[(adcchannel==data.boardIndexAndChannel) & (data.phaMax>=energylimitslow) & (data.phaMax<energylimitshigh)].reset_index(drop=True)
    
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
    
    hist = np.histogram(eventtime, bins=bin_num)
    crate = hist[0]
    
    crate[crate==0] = np.mean(crate)
    
    #output
    result = pd.DataFrame({'time': [], 'score': []})
    
    #for j in tqdm(range(w+k, bin_num-lag+1)):
    for j in range(w+k, bin_num-lag+1):
        (rireki, test) = slidewindow(crate, w, k, lag, j)
        result = result.append(pd.DataFrame({'time': [j], 'score': [score(rireki, test, m)]}))
    
    if result.score.max() > 0.5:
        print(fitsfile)
    #shutsuryoku
    #result.to_csv('result.csv')
    