#/usr/bin/env python
'''
Date: Sep 2, 2020

Take landsea mask from wrf output and construct input.csv by all ocean grid

Zhenning LI

'''

import numpy as np
import csv

if __name__ == "__main__":
    
    init_height=100 
    xlat1d=np.linspace(17.5,22.5,100)
    xlon1d=np.linspace(115,120,100)
    igrid=0
    with open('../input/input_GBA_d01.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for ilat in xlat1d:
            for ilon in xlon1d:
                spamwriter.writerow([igrid, ilat, ilon, init_height])
                igrid=igrid+1
        
